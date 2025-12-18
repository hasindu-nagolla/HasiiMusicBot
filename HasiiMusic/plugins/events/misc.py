# ==============================================================================
# misc.py - Miscellaneous Event Handlers
# ==============================================================================
# This plugin handles various bot events and background tasks.
#
# Events:
# - Voice chat started/ended - Auto-stop playback
# - Bot mentioned - Send info message
# - Auto-leave - Remove inactive assistants from groups every 30 minutes
#
# Features:
# - Automatic cleanup of inactive voice chat sessions
# - Bot promotion reminders
# - Keep assistants from cluttering unused groups
# ==============================================================================

import asyncio
import time

from pyrogram import enums, filters, types

from HasiiMusic import tune, app, config, db, lang, queue, tasks, userbot, yt
from HasiiMusic.helpers import buttons


@app.on_message(filters.video_chat_started, group=19)
@app.on_message(filters.video_chat_ended, group=20)
async def _watcher_vc(_, m: types.Message):
    await tune.stop(m.chat.id)


async def auto_leave():
    while True:
        await asyncio.sleep(1800)
        for ub in userbot.clients:
            left = 0
            try:
                for dialog in await ub.get_dialogs():
                    chat_id = dialog.chat.id
                    if left >= 20:
                        break
                    # Skip logger and any excluded chats
                    excluded = [app.logger] + config.EXCLUDED_CHATS
                    if chat_id in excluded:
                        continue
                    if dialog.chat.type in [
                        enums.ChatType.GROUP,
                        enums.ChatType.SUPERGROUP,
                    ]:
                        if chat_id in db.active_calls:
                            continue
                        await ub.leave_chat(chat_id)
                        left += 1
                    await asyncio.sleep(5)
            except:
                continue


async def track_time():
    while True:
        await asyncio.sleep(1)
        for chat_id in db.active_calls:
            try:
                if not await db.playing(chat_id):
                    continue
                media = queue.get_current(chat_id)
                if not media:
                    continue
                # Ensure media.time is initialized
                if not hasattr(media, 'time') or media.time is None:
                    media.time = 0
                media.time += 1
            except Exception as e:
                # Log error but continue tracking other chats
                print(f"track_time error for chat {chat_id}: {e}")
                continue


async def update_timer(length=10):
    """Update progress bar every 7 seconds for all active chats independently."""
    chat_tasks = {}  # Track individual chat update tasks

    async def _preload_next(chat_id, next_media):
        """Pre-download next song without blocking timer updates."""
        try:
            next_media.file_path = await yt.download(next_media.id, video=False)
        except Exception as e:
            print(f"Preload error for chat {chat_id}: {e}")

    async def update_chat_timer(chat_id):
        """Update timer for a specific chat every 7 seconds."""
        while True:
            try:
                await asyncio.sleep(7)

                # Check if chat is still active and playing
                if chat_id not in db.active_calls or not await db.playing(chat_id):
                    break

                media = queue.get_current(chat_id)
                if not media:
                    break

                # Ensure media.time is initialized
                if not hasattr(media, 'time') or media.time is None:
                    media.time = 0

                duration, message_id = media.duration_sec, media.message_id
                if not duration or not message_id:
                    continue

                played = media.time
                remaining = duration - played
                pos = min(int((played / duration) * length), length - 1)
                timer_bar = "—" * pos + "●" + "—" * (length - pos - 1)

                # Pre-download next song if needed (don't block timer update)
                if remaining <= 30:
                    next = queue.get_next(chat_id, check=True)
                    if next and not next.file_path:
                        asyncio.create_task(_preload_next(chat_id, next))

                if remaining < 10:
                    remove = True
                    timer_text = timer_bar
                else:
                    remove = False
                    played_time = time.strftime('%M:%S', time.gmtime(played))
                    total_time = time.strftime('%M:%S', time.gmtime(duration))
                    timer_text = f"{played_time} {timer_bar} {total_time}"

                await app.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=buttons.controls(
                        chat_id=chat_id, timer=timer_text, remove=remove),
                )
            except Exception as e:
                error_str = str(e)
                # Silently ignore expected Telegram API errors
                if not any(err in error_str for err in [
                    "MESSAGE_NOT_MODIFIED",
                    "MESSAGE_ID_INVALID",
                    "MESSAGE_DELETE",
                    "CHAT_ADMIN_REQUIRED"
                ]):
                    print(f"update_timer error for chat {chat_id}: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    # Monitor and spawn individual chat timers
    while True:
        await asyncio.sleep(2)  # Check for new chats every 2 seconds

        for chat_id in list(db.active_calls):
            # Start timer for new active chats
            if chat_id not in chat_tasks:
                task = asyncio.create_task(update_chat_timer(chat_id))
                chat_tasks[chat_id] = task

        # Clean up finished tasks
        finished_chats = [
            chat_id for chat_id, task in chat_tasks.items()
            if task.done() or chat_id not in db.active_calls
        ]
        for chat_id in finished_chats:
            chat_tasks.pop(chat_id, None)


async def vc_watcher(sleep=15):
    """Leave voice chat after 5 minutes if no users are listening."""
    alone_times = {}  # Track when assistant started being alone in VC
    LEAVE_TIMEOUT = 300  # 5 minutes in seconds (hardcoded)
    
    while True:
        await asyncio.sleep(sleep)
        current_time = time.time()
        
        for chat_id in list(db.active_calls):
            try:
                # Check if auto-leave is enabled for this chat
                if not await db.get_autoleave(chat_id):
                    alone_times.pop(chat_id, None)
                    continue
                
                client = await db.get_assistant(chat_id)
                participants = await client.get_participants(chat_id)
                
                # Check if only assistant is in VC (participants < 2 means only assistant)
                if len(participants) < 2:
                    # Start tracking alone time
                    if chat_id not in alone_times:
                        alone_times[chat_id] = current_time
                    else:
                        # Check if alone for 5 minutes
                        alone_duration = current_time - alone_times[chat_id]
                        if alone_duration >= LEAVE_TIMEOUT:
                            _lang = await lang.get_lang(chat_id)
                            try:
                                current_media = queue.get_current(chat_id)
                                if current_media and current_media.message_id:
                                    sent = await app.edit_message_reply_markup(
                                        chat_id=chat_id,
                                        message_id=current_media.message_id,
                                        reply_markup=buttons.controls(
                                            chat_id=chat_id, status=_lang["stopped"], remove=True
                                        ),
                                    )
                                    await sent.reply_text(_lang["auto_left"])
                            except:
                                pass
                            
                            # Stop playback and leave
                            await tune.stop(chat_id)
                            await client.leave_call(chat_id, close=False)
                            alone_times.pop(chat_id, None)
                else:
                    # Reset timer if users join
                    alone_times.pop(chat_id, None)
                    
            except Exception as e:
                print(f"vc_watcher error for chat {chat_id}: {e}")
                alone_times.pop(chat_id, None)
                continue


# Always run VC watcher to check for empty voice chats
tasks.append(asyncio.create_task(vc_watcher()))
if config.AUTO_LEAVE:
    tasks.append(asyncio.create_task(auto_leave()))
tasks.append(asyncio.create_task(track_time()))
tasks.append(asyncio.create_task(update_timer()))
