"""
# ==============================================================================
# player.py - Calls Playback Engine
# ==============================================================================
# This file manages the core logic for starting streams in PyTgCalls.
# Features:
# - Validates media and fetches thumbnail
# - Sets up ffmpeg arguments based on media type and seek time
# - Handles PyTgCalls start with robust retry logic (FloodWaits, ghost streams)
# - Sends UI messages with playback status
# ==============================================================================
"""

import asyncio
import re
from ntgcalls import ConnectionNotFound, TelegramServerError, TransportParseException
from pyrogram import enums, errors
from pyrogram.types import Message
from pytgcalls import exceptions, types

from HasiiMusic import app, config, db, lang, logger, preload
from HasiiMusic.helpers import Media, Track, buttons, thumb

class CallPlayer:
    def __init__(self, controller):
        self.controller = controller

    async def play_media(
        self,
        chat_id: int,
        message: Message | None,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        async with self.controller.get_lock(chat_id):
            await self._play_media_impl(
                chat_id, message, media, seek_time
            )

    async def _play_media_impl(
        self,
        chat_id: int,
        message: Message | None,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        """Play media in voice chat.

        Args:
            chat_id: Where to stream audio
            message: Message to edit/delete (if any)
            media: Media object to play
            seek_time: Position to seek to (seconds)
        """
        client = await db.get_assistant(chat_id)
        _lang = await lang.get_lang(chat_id)

        # Generate thumbnail only if THUMB_GEN is enabled. otherwise use default
        if config.THUMB_GEN and isinstance(media, Track):
            if not getattr(media, "thumbnail", None) and re.fullmatch(r"[A-Za-z0-9_-]{11}", media.id):
                media.thumbnail = f"https://i.ytimg.com/vi/{media.id}/hqdefault.jpg"
            _thumb = await thumb.generate(media)
        else:
            _thumb = config.DEFAULT_THUMB

        if not media.file_path:
            if message:
                return await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
            else:
                logger.error(f"No file path for media in {chat_id}")
                return

        # make sure this is a valid group chat
        try:
            chat = await app.get_chat(chat_id)
            if chat.type not in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                logger.error(f"Invalid chat type for {chat_id}: {chat.type}")
                if message:
                    await message.edit_text("❌ ᴄᴀɴ ᴏɴʟʏ ᴘʟᴀʏ ɪɴ ɢʀᴏᴜᴘꜱ.")
                return
        except errors.RPCError as e:
            raise

        # Configure audio stream with optimized buffering for lag-free playback. larger buffers help reduce playback lag
        if seek_time > 1:
            # seek to the position first and keep the buffers
            ffmpeg_params = f"-ss {seek_time} -probesize 10M -analyzeduration 5M -rtbufsize 5M -fflags +genpts+igndts"
        else:
            ffmpeg_params = "-probesize 10M -analyzeduration 5M -rtbufsize 5M -fflags +genpts+igndts -sync ext"

        is_video = getattr(media, "video", False)
        video_flags = (
            types.MediaStream.Flags.AUTO_DETECT
            if is_video
            else types.MediaStream.Flags.IGNORE
        )

        kwargs = {
            "media_path": media.file_path,
            "audio_parameters": types.AudioQuality.STUDIO,
            "audio_flags": types.MediaStream.Flags.REQUIRED,
            "video_flags": video_flags,
            "ffmpeg_parameters": ffmpeg_params,
        }
        
        if is_video:
            # use VIDEO_MAX_HEIGHT for the playback resolution.
            # lower resolution and FPS use less CPU.
            h = config.VIDEO_MAX_HEIGHT or 720
            if h <= 360:
                w, fps = 640, 15
            elif h <= 480:
                w, fps = 854, 20
            elif h <= 720:
                w, fps = 1280, 25
            else:
                w, fps = 1920, 30
            kwargs["video_parameters"] = types.raw.VideoParameters(
                width=w, height=h, frame_rate=fps,
            )
            
        stream = types.MediaStream(**kwargs)

        try:
            # ALWAYS attempt to leave the call before starting a new stream to clear ghost streams
            # even if db.get_call says False, because PyTgCalls might be out of sync
            await client.leave_call(chat_id, close=False)
            await asyncio.sleep(0.3)  # give PyTgCalls a moment to finish leaving
        except (ConnectionNotFound, exceptions.NotInCallError):
            pass
        except Exception as e:
            logger.debug(f"Error leaving call for ghost stream prevention in {chat_id}: {e}")

        max_retries = 3
        retry_delay = 1

        try:
            for attempt in range(max_retries):
                try:
                    await client.play(
                        chat_id=chat_id,
                        stream=stream,
                        config=types.GroupCallConfig(auto_start=True),
                    )
                    break
                except (exceptions.NoActiveGroupCall, errors.RPCError) as e:
                    error_msg = str(e)
                    if "GROUPCALL_INVALID" in error_msg or "GROUPCALL" in error_msg or isinstance(e, exceptions.NoActiveGroupCall):
                        if attempt < max_retries - 1:
                            logger.debug(
                                f"Group call transitioning for {chat_id}, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            raise
                    else:
                        raise
                except TransportParseException:
                    # WebRTC transport negotiation failed, VC may have ended
                    if attempt < max_retries - 1:
                        logger.debug(
                            f"Transport not found for {chat_id}, retrying... (attempt {attempt + 1}/{max_retries})")
                        try:
                            await client.leave_call(chat_id, close=False)
                        except Exception:
                            pass
                        await asyncio.sleep(retry_delay + 1)
                        continue
                    else:
                        raise
                except Exception as e:
                    error_msg = str(e).lower()
                    if "cannot be initialized more than once" in error_msg or "connection" in error_msg:
                        if attempt < max_retries - 1:
                            logger.debug(
                                f"Connection error for {chat_id}, leaving and retrying... (attempt {attempt + 1}/{max_retries})")
                            try:
                                await client.leave_call(chat_id, close=False)
                                await asyncio.sleep(retry_delay)
                            except Exception:
                                pass
                            continue
                        else:
                            raise
                    else:
                        raise

            if seek_time:
                media.time = seek_time
            else:
                media.time = 1

            if not seek_time:
                await db.add_call(chat_id)
                text = _lang["play_media"].format(
                    media.url,
                    media.title,
                    media.duration,
                    media.user,
                )
                if getattr(media, "playlist_name", None):
                    pl_url = getattr(media, "playlist_url", None)
                    pl_type = getattr(media, "playlist_type", None)
                    if pl_type == "album":
                        label = "ᴀʟʙᴜᴍ"
                    elif pl_type == "artist":
                        label = "ᴀʀᴛɪꜱᴛ"
                    else:
                        label = "ᴘʟᴀʏʟɪꜱᴛ"

                    if pl_url:
                        pl_display = f"<a href={pl_url}>{media.playlist_name}</a>"
                    else:
                        pl_display = media.playlist_name

                    text = text.replace(
                        "➤ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b>",
                        f"➤ <b>{label} :</b> {pl_display}\n➤ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b>",
                    )
                if not getattr(media, "is_live", False) and getattr(media, "duration_sec", 0):
                    import time as time_module
                    played = media.time
                    duration = media.duration_sec
                    bar_length = 12
                    if duration == 0:
                        percentage = 0
                    else:
                        percentage = min((played / duration) * 100, 100)
                    filled = int(round(bar_length * percentage / 100))
                    timer_bar = "—" * filled + "●" + \
                        "—" * (bar_length - filled)
                    if duration >= 3600:
                        played_time = time_module.strftime(
                            '%H:%M:%S', time_module.gmtime(played))
                        total_time = time_module.strftime(
                            '%H:%M:%S', time_module.gmtime(duration))
                    else:
                        played_time = time_module.strftime(
                            '%M:%S', time_module.gmtime(played))
                        total_time = time_module.strftime(
                            '%M:%S', time_module.gmtime(duration))
                    timer_text = f"{played_time} {timer_bar} {total_time}"
                    keyboard = buttons.controls(chat_id, timer=timer_text)
                else:
                    keyboard = buttons.controls(chat_id)

                if message:
                    try:
                        await message.delete()
                    except Exception:
                        pass

                lock = self.controller.get_lock(chat_id)
                current_session = self.controller._session_gen.get(chat_id, 0)
                lock.release()
                try:
                    sent_photo = await self.controller._utils.send_photo_with_retry(
                        chat_id=chat_id,
                        photo=_thumb,
                        caption=text,
                        reply_markup=keyboard,
                    )
                finally:
                    await lock.acquire()
                    
                if self.controller._session_gen.get(chat_id, 0) != current_session:
                    logger.info(f"Session invalidated during send_photo for {chat_id}")
                    return

                if sent_photo:
                    media.message_id = sent_photo.id

                try:
                    asyncio.create_task(
                        preload.start_preload(chat_id, count=2))
                except Exception as e:
                    logger.debug(f"Error starting preload for {chat_id}: {e}")
        except FileNotFoundError:
            if message:
                try:
                    await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
                except Exception:
                    pass
            await self.controller._queue._play_next_impl(chat_id)
        except exceptions.NoActiveGroupCall:
            await self.controller._controls._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_vc_disabled"])
                except Exception:
                    pass
        except errors.RPCError as e:
            error_str = str(e)

            if any(x in error_str for x in ["CHAT_ADMIN_REQUIRED", "phone.CreateGroupCall", "GROUPCALL_FORBIDDEN", "GROUPCALL_CREATE_FORBIDDEN", "VOICE_MESSAGES_FORBIDDEN"]):
                await self.controller._controls._stop_impl(chat_id)
                if message:
                    try:
                        await message.edit_text(_lang["error_vc_disabled"])
                    except Exception:
                        pass
            elif "GROUPCALL_INVALID" in error_str or "GROUPCALL" in error_str:
                await self.controller._controls._stop_impl(chat_id)
                if message:
                    try:
                        await message.edit_text(_lang["error_no_call"])
                    except Exception:
                        pass
            else:
                logger.error(f"RPC error in play_media for {chat_id}: {e}")
                await self.controller._controls._stop_impl(chat_id)
        except exceptions.NoAudioSourceFound:
            if message:
                try:
                    await message.edit_text(_lang["error_no_audio"])
                except Exception:
                    pass
            await self.controller._queue._play_next_impl(chat_id)
        except TransportParseException:
            # all retries failed, so the voice chat is probably gone
            logger.warning(f"Transport not found for {chat_id} after retries, stopping.")
            await self.controller._controls._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_no_call"])
                except Exception:
                    pass
        except (ConnectionNotFound, TelegramServerError):
            await self.controller._controls._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_tg_server"])
                except Exception:
                    pass
        except TimeoutError as e:
            error_msg = str(e)
            logger.warning(
                f"⏱️ Timeout joining voice chat {chat_id}: {error_msg}")
            await self.controller._controls._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(
                        "⏱️ <b>ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛɪᴍᴇᴅ ᴏᴜᴛ!</b>\n\n"
                        "<blockquote>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɴᴇᴛᴡᴏʀᴋ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote>"
                    )
                except Exception:
                    pass
            await asyncio.sleep(2)
            await self.controller._queue._play_next_impl(chat_id)
        except Exception as e:
            logger.error(
                f"Unexpected error in play_media for {chat_id}: {e}", exc_info=True)
            await self.controller._controls._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(f"❌ Playback error: {str(e)[:100]}")
                except Exception:
                    pass
