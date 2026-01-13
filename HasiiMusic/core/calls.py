# ==============================================================================
# calls.py - Voice Call Handler (PyTgCalls Integration)
# ==============================================================================
# This file manages voice/video chat functionality using PyTgCalls.
# Features:
# - Stream audio/video to Telegram voice chats
# - Playback controls (play, pause, resume, stop, seek)
# - Queue management (play next track automatically)
# - Multi-assistant support (load balancing)
# - Live stream support
# - Thumbnail updates during playback
# ==============================================================================

import asyncio
import logging
from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import errors
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

from HasiiMusic import app, config, db, lang, logger, queue, userbot, yt
from HasiiMusic.helpers import Media, Track, buttons, thumb

# Suppress pytgcalls UpdateGroupCall errors (library bug - harmless)
class UpdateGroupCallFilter(logging.Filter):
    def filter(self, record):
        return 'UpdateGroupCall' not in record.getMessage()

logging.getLogger('pyrogram.dispatcher').addFilter(UpdateGroupCallFilter())


class TgCall(PyTgCalls):
    def __init__(self):
        self.clients = []

    async def _edit_media_with_retry(self, message: Message, media_obj: InputMediaPhoto, reply_markup):
        """Edit media with basic FloodWait handling."""
        try:
            return await message.edit_media(media=media_obj, reply_markup=reply_markup)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                return await message.edit_media(media=media_obj, reply_markup=reply_markup)
            except Exception:
                return None
        except errors.MessageNotModified:
            return None
        except Exception:
            return None

    async def _send_photo_with_retry(self, chat_id: int, photo, caption: str, reply_markup):
        """Send photo with FloodWait handling."""
        try:
            return await app.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
            )
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                return await app.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup,
                )
            except Exception:
                return None
        except Exception:
            return None

    async def pause(self, chat_id: int) -> bool:
        client = await db.get_assistant(chat_id)
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        client = await db.get_assistant(chat_id)
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        client = await db.get_assistant(chat_id)
        try:
            queue.clear(chat_id)
            await db.remove_call(chat_id)
        except Exception as e:
            logger.warning(f"Error clearing queue/call for {chat_id}: {e}")

        try:
            await client.leave_call(chat_id, close=False)
            # Small delay to let group call state stabilize after leaving
            await asyncio.sleep(0.5)
        except (ConnectionNotFound, exceptions.NotInCallError):
            # Expected: userbot is not in a call
            pass
        except Exception as e:
            # Only log unexpected errors
            error_msg = str(e)
            if ("not in a call" not in error_msg.lower() and 
                "GROUPCALL_FORBIDDEN" not in error_msg and
                "No active group call" not in error_msg and
                "not in the group call" not in error_msg.lower()):
                logger.warning(f"Error leaving call for {chat_id}: {e}")

    async def play_media(
        self,
        chat_id: int,
        message: Message,
        media: Media | Track,
        seek_time: int = 0,
        video: bool = False,
    ) -> None:
        client = await db.get_assistant(chat_id)
        _lang = await lang.get_lang(chat_id)
        _thumb = (
            await thumb.generate(media)
            if isinstance(media, Track)
            else config.DEFAULT_THUMB
        )

        if not media.file_path:
            return await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))

        # Configure stream based on video or audio mode
        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.STUDIO,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=types.MediaStream.Flags.REQUIRED if video else types.MediaStream.Flags.IGNORE,
            ffmpeg_parameters=f"-ss {seek_time}" if seek_time > 1 else None,
        )
        
        # Retry logic for race conditions when stopping/starting quickly
        max_retries = 3
        retry_delay = 1  # seconds
        
        try:
            for attempt in range(max_retries):
                try:
                    await client.play(
                        chat_id=chat_id,
                        stream=stream,
                        config=types.GroupCallConfig(auto_start=True),
                    )
                    # Success - break retry loop
                    break
                except (exceptions.NoActiveGroupCall, errors.RPCError) as e:
                    error_msg = str(e)
                    # Check if it's a group call state error
                    if "GROUPCALL_INVALID" in error_msg or "GROUPCALL" in error_msg or isinstance(e, exceptions.NoActiveGroupCall):
                        if attempt < max_retries - 1:
                            # Wait for group call state to stabilize
                            logger.info(f"Group call transitioning for {chat_id}, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            # Final attempt failed
                            raise
                    else:
                        # Different error, don't retry
                        raise
                
            # Initialize media.time based on seek position
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
                # Create initial timer display
                if not media.is_live and media.duration_sec:
                    import time as time_module
                    played = media.time  # Use actual media.time value
                    duration = media.duration_sec
                    # Build progress bar with original style
                    bar_length = 12
                    if duration == 0:
                        percentage = 0
                    else:
                        percentage = min((played / duration) * 100, 100)
                    filled = int(round(bar_length * percentage / 100))
                    timer_bar = "—" * filled + "●" + "—" * (bar_length - filled)
                    # Format time properly with hours support
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
                updated = await self._edit_media_with_retry(
                    message,
                    InputMediaPhoto(media=_thumb, caption=text),
                    keyboard,
                )

                if updated is None:
                    sent_photo = await self._send_photo_with_retry(
                        chat_id=chat_id,
                        photo=_thumb,
                        caption=text,
                        reply_markup=keyboard,
                    )
                    if sent_photo:
                        media.message_id = sent_photo.id
        except FileNotFoundError:
            try:
                await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
            except Exception:
                pass
            await self.play_next(chat_id)
        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            try:
                await message.edit_text(_lang["error_no_call"])
            except Exception:
                pass
        except errors.RPCError as e:
            # Handle Telegram API errors (GROUPCALL_INVALID, CHAT_ADMIN_REQUIRED, etc.)
            error_str = str(e)
            if "CHAT_ADMIN_REQUIRED" in error_str or "phone.CreateGroupCall" in error_str:
                # Voice chat is disabled or assistant doesn't have admin permissions
                await self.stop(chat_id)
                try:
                    await message.edit_text(_lang.get("error_vc_disabled", _lang["error_no_call"]))
                except Exception:
                    pass
            elif "GROUPCALL_INVALID" in error_str or "GROUPCALL" in error_str:
                await self.stop(chat_id)
                try:
                    await message.edit_text(_lang["error_no_call"])
                except Exception:
                    pass
            else:
                # Log but don't crash for other RPC errors
                logger.error(f"RPC error in play_media for {chat_id}: {e}")
                await self.stop(chat_id)
        except exceptions.NoAudioSourceFound:
            error_msg = _lang["error_no_video"] if video else _lang["error_no_audio"]
            try:
                await message.edit_text(error_msg)
            except Exception:
                pass
            await self.play_next(chat_id)
        except (ConnectionNotFound, TelegramServerError):
            await self.stop(chat_id)
            try:
                await message.edit_text(_lang["error_tg_server"])
            except Exception:
                pass
        except Exception as e:
            # Catch all other exceptions to prevent bot crash
            logger.error(f"Unexpected error in play_media for {chat_id}: {e}", exc_info=True)
            await self.stop(chat_id)
            try:
                await message.edit_text(f"❌ Playback error: {str(e)[:100]}")
            except Exception:
                pass

    async def replay(self, chat_id: int) -> None:
        try:
            if not await db.get_call(chat_id):
                return

            media = queue.get_current(chat_id)
            _lang = await lang.get_lang(chat_id)
            msg = await app.send_message(chat_id=chat_id, text=_lang["play_again"])
            is_video = getattr(media, 'video', False)
            await self.play_media(chat_id, msg, media, video=is_video)
        except Exception as e:
            logger.error(f"Error in replay for {chat_id}: {e}", exc_info=True)

    async def seek_stream(self, chat_id: int, seconds: int) -> bool:
        """Seek to a specific position in the current stream."""
        try:
            if not await db.get_call(chat_id):
                return False

            media = queue.get_current(chat_id)
            if not media or media.is_live:
                return False

            client = await db.get_assistant(chat_id)
            _lang = await lang.get_lang(chat_id)
            
            # Update media time
            media.time = seconds
            
            # Get message to update
            msg = await app.get_messages(chat_id, media.message_id)
            if not msg:
                msg = await app.send_message(chat_id=chat_id, text=_lang["seeking"])
            
            # Replay from new position with correct video mode
            is_video = getattr(media, 'video', False)
            await self.play_media(chat_id, msg, media, seek_time=seconds, video=is_video)
            return True
        except Exception as e:
            logger.error(f"Error in seek_stream for {chat_id}: {e}", exc_info=True)
            return False

    async def play_next(self, chat_id: int) -> None:
        try:
            if not await db.get_call(chat_id):
                return

            # Check loop mode
            loop_mode = await db.get_loop(chat_id)
            
            if loop_mode == 1:
                # Single track loop - replay current track
                media = queue.get_current(chat_id)
                if media:
                    _lang = await lang.get_lang(chat_id)
                    msg = await app.send_message(chat_id=chat_id, text=_lang["play_again"])
                    is_video = getattr(media, 'video', False)
                    await self.play_media(chat_id, msg, media, video=is_video)
                    return
            
            media = queue.get_next(chat_id)
            
            # If queue loop and no more tracks, start from beginning
            if not media and loop_mode == 10:
                all_items = queue.get_all(chat_id)
                if all_items:
                    # Reset queue to beginning
                    first_track = all_items[0]
                    _lang = await lang.get_lang(chat_id)
                    msg = await app.send_message(chat_id=chat_id, text="🔁 Looping queue...")
                    if not first_track.file_path:
                        is_live = getattr(first_track, 'is_live', False)
                        is_video = getattr(first_track, 'video', False)
                        first_track.file_path = await yt.download(first_track.id, video=is_video, is_live=is_live)
                    first_track.message_id = msg.id
                    is_video = getattr(first_track, 'video', False)
                    await self.play_media(chat_id, msg, first_track, video=is_video)
                    return
            
            try:
                if media and media.message_id:
                    await app.delete_messages(
                        chat_id=chat_id,
                        message_ids=media.message_id,
                        revoke=True,
                    )
                    media.message_id = 0
            except Exception as e:
                logger.debug(f"Could not delete previous message in {chat_id}: {e}")

            if not media:
                return await self.stop(chat_id)

            _lang = await lang.get_lang(chat_id)
            msg = await app.send_message(chat_id=chat_id, text=_lang["play_next"])
            if not media.file_path:
                is_live = getattr(media, 'is_live', False)
                is_video = getattr(media, 'video', False)
                media.file_path = await yt.download(media.id, video=is_video, is_live=is_live)
                if not media.file_path:
                    await self.stop(chat_id)
                    try:
                        await msg.edit_text(
                            _lang["error_no_file"].format(config.SUPPORT_CHAT)
                        )
                    except Exception:
                        pass
                    return

            media.message_id = msg.id
            is_video = getattr(media, 'video', False)
            await self.play_media(chat_id, msg, media, video=is_video)
        except Exception as e:
            logger.error(f"Error in play_next for {chat_id}: {e}", exc_info=True)
            # Try to stop the call gracefully
            try:
                await self.stop(chat_id)
            except Exception:
                pass

    async def ping(self) -> float:
        pings = [client.ping for client in self.clients]
        return round(sum(pings) / len(pings), 2)

    async def decorators(self, client: PyTgCalls) -> None:
        for client in self.clients:
            @client.on_update()
            async def update_handler(_, update: types.Update) -> None:
                if isinstance(update, types.StreamEnded):
                    if update.stream_type == types.StreamEnded.Type.AUDIO:
                        await self.play_next(update.chat_id)
                elif isinstance(update, types.ChatUpdate):
                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:
                        await self.stop(update.chat_id)

    async def boot(self) -> None:
        PyTgCallsSession.notice_displayed = True
        for ub in userbot.clients:
            # Increased cache for better performance
            client = PyTgCalls(ub, cache_duration=300)
            await client.start()
            self.clients.append(client)
            await self.decorators(client)
        logger.info("📞 PyTgCalls client(s) started.")
