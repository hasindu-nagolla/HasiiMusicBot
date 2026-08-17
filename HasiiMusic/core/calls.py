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
from ntgcalls import ConnectionNotFound, TelegramServerError, TransportParseException
from pyrogram import enums, errors
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

from HasiiMusic import app, config, db, lang, logger, preload, queue, userbot, yt
from HasiiMusic.helpers import Media, Track, buttons, thumb

# hide harmless PyTgCalls errors from the logs
class PyTgCallsErrorFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # ignore UpdateGroupCall errors
        if 'UpdateGroupCall' in msg:
            return False
        # ignore connection errors after a call ends
        if 'Connection with chat id' in msg and 'not found' in msg:
            return False
        # ignore InvalidStateError from PyTgCalls clear_call
        if 'invalid state' in msg.lower() and 'set_exception' in msg:
            return False
        return True


logging.getLogger('pyrogram.dispatcher').addFilter(PyTgCallsErrorFilter())


class TgCall(PyTgCalls):
    def __init__(self):
        self.clients = []
        self._chat_locks = {}  # one lock for each chat to avoid playback conflicts
        self._session_gen = {}
        self._track_index = {}
        self._pending_transitions = set()

    def get_lock(self, chat_id: int) -> asyncio.Lock:
        if chat_id not in self._chat_locks:
            self._chat_locks[chat_id] = asyncio.Lock()
        return self._chat_locks[chat_id]

    async def _edit_media_with_retry(self, message: Message, media_obj: InputMediaPhoto, reply_markup):
        #edit media and handle FloodWait
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
        #Send photo with FloodWait handling.
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
        async with self.get_lock(chat_id):
            client = await db.get_assistant(chat_id)
            try:
                await client.pause(chat_id)
                await db.playing(chat_id, paused=True)
                return True
            except (ConnectionNotFound, exceptions.NotInCallError):
                await db.playing(chat_id, paused=False)
                await db.remove_call(chat_id)
                queue.clear(chat_id)
                logger.warning(
                    f"Pause requested but assistant not in call for {chat_id}, syncing state")
                return False
            except Exception as e:
                await db.playing(chat_id, paused=False)
                logger.error(f"Pause failed for {chat_id}: {e}")
                return False

    async def resume(self, chat_id: int) -> bool:
        async with self.get_lock(chat_id):
            client = await db.get_assistant(chat_id)
            try:
                await client.resume(chat_id)
                await db.playing(chat_id, paused=False)
                return True
            except (ConnectionNotFound, exceptions.NotInCallError):
                await db.playing(chat_id, paused=False)
                await db.remove_call(chat_id)
                queue.clear(chat_id)
                logger.warning(
                    f"Resume requested but assistant not in call for {chat_id}, syncing state")
                return False
            except Exception as e:
                logger.error(f"Resume failed for {chat_id}: {e}")
                return False

    async def stop(self, chat_id: int) -> None:
        async with self.get_lock(chat_id):
            await self._stop_impl(chat_id)

    async def _stop_impl(self, chat_id: int) -> None:
        self._session_gen[chat_id] = self._session_gen.get(chat_id, 0) + 1
        client = await db.get_assistant(chat_id)

        # Cancel any active preload tasks when stopping
        try:
            await preload.cancel_preload(chat_id)
        except Exception as e:
            logger.debug(f"Error cancelling preload for {chat_id}: {e}")

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
            # the userbot is already out of the call
            pass
        except Exception as e:
            # unexpected errors
            error_msg = str(e).lower()
            if not any(ignore in error_msg for ignore in [
                "not in a call",
                "not in the group call",
                "groupcall_forbidden",
                "no active group call",
                "call was already stopped",
                "call already disconnected"
            ]):
                logger.warning(f"Error leaving call for {chat_id}: {e}")

    async def play_media(
        self,
        chat_id: int,
        message: Message | None,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        async with self.get_lock(chat_id):
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
                if not media.is_live and media.duration_sec:
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

                lock = self.get_lock(chat_id)
                current_session = self._session_gen.get(chat_id, 0)
                lock.release()
                try:
                    sent_photo = await self._send_photo_with_retry(
                        chat_id=chat_id,
                        photo=_thumb,
                        caption=text,
                        reply_markup=keyboard,
                    )
                finally:
                    await lock.acquire()
                    
                if self._session_gen.get(chat_id, 0) != current_session:
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
            await self._play_next_impl(chat_id)
        except exceptions.NoActiveGroupCall:
            await self._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_vc_disabled"])
                except Exception:
                    pass
        except errors.RPCError as e:
            error_str = str(e)

            if any(x in error_str for x in ["CHAT_ADMIN_REQUIRED", "phone.CreateGroupCall", "GROUPCALL_FORBIDDEN", "GROUPCALL_CREATE_FORBIDDEN", "VOICE_MESSAGES_FORBIDDEN"]):
                await self._stop_impl(chat_id)
                if message:
                    try:
                        await message.edit_text(_lang["error_vc_disabled"])
                    except Exception:
                        pass
            elif "GROUPCALL_INVALID" in error_str or "GROUPCALL" in error_str:
                await self._stop_impl(chat_id)
                if message:
                    try:
                        await message.edit_text(_lang["error_no_call"])
                    except Exception:
                        pass
            else:
                logger.error(f"RPC error in play_media for {chat_id}: {e}")
                await self._stop_impl(chat_id)
        except exceptions.NoAudioSourceFound:
            if message:
                try:
                    await message.edit_text(_lang["error_no_audio"])
                except Exception:
                    pass
            await self._play_next_impl(chat_id)
        except TransportParseException:
            # all retries failed, so the voice chat is probably gone
            logger.warning(f"Transport not found for {chat_id} after retries, stopping.")
            await self._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_no_call"])
                except Exception:
                    pass
        except (ConnectionNotFound, TelegramServerError):
            await self._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(_lang["error_tg_server"])
                except Exception:
                    pass
        except TimeoutError as e:
            error_msg = str(e)
            logger.warning(
                f"⏱️ Timeout joining voice chat {chat_id}: {error_msg}")
            await self._stop_impl(chat_id)
            if message:
                try:
                    await message.edit_text(
                        "⏱️ <b>ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛɪᴍᴇᴅ ᴏᴜᴛ!</b>\n\n"
                        "<blockquote>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɴᴇᴛᴡᴏʀᴋ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote>"
                    )
                except Exception:
                    pass
            await asyncio.sleep(2)
            await self._play_next_impl(chat_id)
        except Exception as e:
            logger.error(
                f"Unexpected error in play_media for {chat_id}: {e}", exc_info=True)
            await self._stop_impl(chat_id)
            if message:
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
            await self.play_media(chat_id, msg, media)
        except Exception as e:
            logger.error(f"Error in replay for {chat_id}: {e}", exc_info=True)

    async def seek_stream(self, chat_id: int, seconds: int) -> bool:
        """seek to a position in the current stream"""
        try:
            if not await db.get_call(chat_id):
                return False

            media = queue.get_current(chat_id)
            if not media or media.is_live:
                return False

            client = await db.get_assistant(chat_id)
            _lang = await lang.get_lang(chat_id)

            media.time = seconds

            try:
                msg = await app.get_messages(chat_id, media.message_id)
            except Exception:
                msg = None

            if not msg:
                _lang = await lang.get_lang(chat_id)
                msg = await app.send_message(chat_id=chat_id, text=_lang["seeking"])

            await self.play_media(chat_id, msg, media, seek_time=seconds)
            return True
        except Exception as e:
            logger.warning(f"Seek stream failed for {chat_id}: {e}")
            return False

    async def play_next(self, chat_id: int, expected_index: int = None) -> None:
        lock = self.get_lock(chat_id)
        async with lock:
            self._pending_transitions.discard(chat_id)
            if expected_index is not None and self._track_index.get(chat_id, 0) != expected_index:
                logger.info(f"Skipping stale play_next for {chat_id}")
                return
            
            self._track_index[chat_id] = self._track_index.get(chat_id, 0) + 1
            await self._play_next_impl(chat_id)

    async def _play_next_impl(self, chat_id: int) -> None:
            try:
                if not await db.get_call(chat_id):
                    return

                loop_mode = await db.get_loop(chat_id)

                if loop_mode == 1:
                    media = queue.get_current(chat_id)
                    if media:
                        _lang = await lang.get_lang(chat_id)
                        try:
                            msg = await app.send_message(chat_id=chat_id, text=_lang["play_again"])
                            await self._play_media_impl(chat_id, msg, media)
                        except errors.ChannelPrivate:
                            logger.warning(
                                f"Bot removed from {chat_id}, cleaning up")
                            try:
                                await self.leave_call(chat_id)
                            except (AttributeError, Exception) as leave_ex:
                                logger.debug(
                                    f"Could not leave call for {chat_id}: {leave_ex}")
                            await db.rm_chat(chat_id)
                        return

                media = queue.get_next(chat_id)

                if not media and loop_mode == 10:
                    all_items = queue.get_all(chat_id)
                    if all_items:
                        first_track = all_items[0]
                        _lang = await lang.get_lang(chat_id)
                        try:
                            msg = await app.send_message(chat_id=chat_id, text="🔁 Looping queue...")
                            if not first_track.file_path:
                                is_live = getattr(first_track, 'is_live', False)
                                lock = self.get_lock(chat_id)
                                current_session = self._session_gen.get(chat_id, 0)
                                lock.release()
                                try:
                                    first_track.file_path = await yt.download(
                                        first_track.id,
                                        is_live=is_live,
                                        video=getattr(first_track, 'video', False),
                                    )
                                finally:
                                    await lock.acquire()
                                
                                if self._session_gen.get(chat_id, 0) != current_session:
                                    logger.info(f"Session invalidated during looping download for {chat_id}")
                                    return
                                if queue.get_current(chat_id) != first_track:
                                    logger.info(f"Queue altered during looping download for {chat_id}")
                                    return
                            first_track.message_id = msg.id
                            await self._play_media_impl(chat_id, msg, first_track)
                        except errors.ChannelPrivate:
                            logger.warning(
                                f"Bot removed from {chat_id}, cleaning up")
                            await self.leave_call(chat_id)
                            await db.rm_chat(chat_id)
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
                    logger.debug(
                        f"Could not delete previous message in {chat_id}: {e}")

                if not media:
                    if config.QUEUE_END_MESSAGE:
                        _lang = await lang.get_lang(chat_id)
                        try:
                            await app.send_message(
                                chat_id=chat_id,
                                text=_lang.get(
                                    "queue_end_message", "✅ Queue finished. Stream ended automatically.")
                            )
                        except Exception as e:
                            logger.debug(
                                f"Could not send queue_end message in {chat_id}: {e}")
                    return await self._stop_impl(chat_id)

                _lang = await lang.get_lang(chat_id)
                msg = None
                if not media.file_path:
                    is_live = getattr(media, 'is_live', False)
                    lock = self.get_lock(chat_id)
                    current_session = self._session_gen.get(chat_id, 0)
                    lock.release()
                    try:
                        media.file_path = await yt.download(
                            media.id,
                            is_live=is_live,
                            video=getattr(media, 'video', False),
                        )
                    finally:
                        await lock.acquire()

                    if self._session_gen.get(chat_id, 0) != current_session:
                        logger.info(f"Session invalidated during play_next download for {chat_id}")
                        return
                    if queue.get_current(chat_id) != media:
                        logger.info(f"Queue altered during play_next download for {chat_id}")
                        return
                    if not media.file_path:
                        await self._stop_impl(chat_id)
                        if msg:
                            try:
                                await msg.edit_text(
                                    _lang["error_no_file"].format(
                                        config.SUPPORT_CHAT)
                                )
                            except Exception:
                                pass
                        return

                try:
                    msg = await app.send_message(chat_id=chat_id, text=_lang["play_next"])
                except errors.FloodWait as fw:
                    # keep playback running even if the status message hits FloodWait
                    logger.warning(
                        f"FloodWait in play_next for {chat_id}: skipping status message ({fw.value}s)")
                    msg = None
                except errors.ChannelPrivate:
                    logger.warning(f"Bot removed from {chat_id}, cleaning up")
                    await self.leave_call(chat_id)
                    await db.rm_chat(chat_id)
                    return
                except Exception as e:
                    logger.error(
                        f"Failed to send play_next message for {chat_id}: {e}")
                    msg = None

                media.message_id = msg.id if msg else 0
                if msg:
                    await self._play_media_impl(chat_id, msg, media)
                else:
                    logger.info(
                        f"Playing next track for {chat_id} without message update")
                    await self._play_media_impl(chat_id, None, media)

                try:
                    asyncio.create_task(
                        preload.start_preload(chat_id, count=2))
                except Exception as e:
                    logger.debug(
                        f"Error starting preload after play_next for {chat_id}: {e}")
            except Exception as e:
                logger.error(
                    f"Error in play_next for {chat_id}: {e}", exc_info=True)
                try:
                    await self._stop_impl(chat_id)
                except Exception:
                    pass

    async def ping(self) -> float:
        pings = [client.ping for client in self.clients]
        return round(sum(pings) / len(pings), 2)

    async def decorators(self, client: PyTgCalls) -> None:
        for client in self.clients:
            @client.on_update()
            async def update_handler(_, update: types.Update) -> None:
                try:
                    if isinstance(update, types.StreamEnded):
                        if update.stream_type == types.StreamEnded.Type.AUDIO:
                            chat_id = update.chat_id
                            expected_index = self._track_index.get(chat_id, 0)
                            if chat_id not in self._pending_transitions:
                                self._pending_transitions.add(chat_id)
                                asyncio.create_task(self.play_next(chat_id, expected_index))
                    elif isinstance(update, types.ChatUpdate):
                        if update.status in [
                            types.ChatUpdate.Status.KICKED,
                            types.ChatUpdate.Status.LEFT_GROUP,
                            types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                        ]:
                            await self.stop(update.chat_id)
                except (ConnectionNotFound, exceptions.NotInCallError, TelegramServerError):
                    return
                except Exception as e:
                    logger.debug(f"Ignoring update handler error: {e}")

    async def boot(self) -> None:
        PyTgCallsSession.notice_displayed = True
        for ub in userbot.clients:
            client = PyTgCalls(ub, cache_duration=100)
            await client.start()
            self.clients.append(client)
            await self.decorators(client)
        logger.info("📞 PyTgCalls client(s) started.")
