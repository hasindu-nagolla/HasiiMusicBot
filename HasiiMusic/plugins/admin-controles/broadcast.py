"""
Broadcast plugin for HasiiMusicBot.

This plugin allows sudo users to broadcast messages to all groups and users
where the bot is active. It supports various options like sending to users only,
excluding groups, and more.

Commands:
    /broadcast <message> [-user] [-nochat]: Broadcast a message
    /stop_gcast, /stop_broadcast: Stop ongoing broadcast

Flags:
    -user: Also send to individual users (in addition to groups)
    -nochat: Don't send to groups (only valid with -user)
"""

import os
import asyncio
from typing import List, Tuple

from pyrogram import enums, errors, filters, types

from HasiiMusic import app, db, lang


# Global flag to track if a broadcast is currently running
broadcasting: bool = False


@app.on_message(filters.command(["broadcast"]) & app.sudoers)
@lang.language()
async def broadcast_message(_, message: types.Message) -> None:
    """
    Broadcast a message to all groups and/or users.
    
    Usage:
        /broadcast <message> - Send to all groups
        /broadcast -user <message> - Send to all groups and users
        /broadcast -nochat -user <message> - Send only to users
    
    Args:
        message: The Telegram message containing the broadcast command.
    
    Returns:
        None
    """
    global broadcasting
    
    # Validate command has message text
    if len(message.command) < 2:
        return await message.reply_text(message.lang["gcast_usage"])
    
    # Check if another broadcast is already running
    if broadcasting:
        return await message.reply_text(message.lang["gcast_active"])
    
    # Parse command: extract flags and actual message
    flags, broadcast_text = _parse_broadcast_command(message.text)
    
    if not broadcast_text:
        return await message.reply_text(message.lang["gcast_usage"])
    
    # Determine recipients based on flags
    groups, users = await _get_broadcast_recipients(flags)
    all_chats = groups + users
    
    if not all_chats:
        return await message.reply_text(
            "❌ No recipients found. Make sure the bot is added to groups or has users."
        )
    
    # Set broadcasting flag
    broadcasting = True
    sent = await message.reply_text(message.lang["gcast_start"])
    
    # Log broadcast initiation
    await _log_broadcast_start(message)
    await asyncio.sleep(5)
    
    # Perform the broadcast
    success_groups, success_users, failed_chats = await _send_broadcast(
        broadcast_text, groups, users, sent
    )
    
    # Reset broadcasting flag
    broadcasting = False
    
    # Send completion message
    await _send_broadcast_completion(
        message, sent, success_groups, success_users, failed_chats
    )


@app.on_message(filters.command(["stop_gcast", "stop_broadcast"]) & app.sudoers)
@lang.language()
async def stop_broadcast(_, message: types.Message) -> None:
    """
    Stop an ongoing broadcast operation.
    
    Args:
        message: The Telegram message containing the stop command.
    
    Returns:
        None
    """
    global broadcasting
    
    if not broadcasting:
        return await message.reply_text(message.lang["gcast_inactive"])
    
    broadcasting = False
    
    # Log broadcast stop
    await (await app.send_message(
        chat_id=app.logger,
        text=message.lang["gcast_stop_log"].format(
            message.from_user.id,
            message.from_user.mention
        )
    )).pin(disable_notification=False)
    
    await message.reply_text(message.lang["gcast_stop"])


def _parse_broadcast_command(text: str) -> Tuple[List[str], str]:
    """
    Parse broadcast command to extract flags and message.
    
    Args:
        text: The full command text.
    
    Returns:
        Tuple of (flags list, message text)
    """
    # Split command and arguments
    parts = text.split(None, 1)[1].split()
    
    # Separate flags (starting with '-') from message words
    flags = [part for part in parts if part.startswith('-')]
    message_parts = [part for part in parts if not part.startswith('-')]
    
    # Reconstruct message from non-flag parts
    message_text = ' '.join(message_parts)
    
    return flags, message_text


async def _get_broadcast_recipients(flags: List[str]) -> Tuple[List[int], List[int]]:
    """
    Get list of groups and users to broadcast to based on flags.
    
    Args:
        flags: List of command flags.
    
    Returns:
        Tuple of (groups list, users list)
    """
    groups = []
    users = []
    
    # Include groups unless -nochat flag is present
    if "-nochat" not in flags:
        groups = await db.get_chats()
    
    # Include users if -user flag is present
    if "-user" in flags:
        users = await db.get_users()
    
    return groups, users


async def _log_broadcast_start(message: types.Message) -> None:
    """
    Log broadcast initiation to logger group.
    
    Args:
        message: The original broadcast command message.
    
    Returns:
        None
    """
    log_message = await app.send_message(
        chat_id=app.logger,
        text=message.lang["gcast_log"].format(
            message.from_user.id,
            message.from_user.mention,
            message.text,
        )
    )
    await log_message.pin(disable_notification=False)


async def _send_broadcast(
    text: str,
    groups: List[int],
    users: List[int],
    status_message: types.Message
) -> Tuple[int, int, str]:
    """
    Send broadcast message to all recipients.
    
    Args:
        text: Message text to broadcast.
        groups: List of group chat IDs.
        users: List of user IDs.
        status_message: Message to update with progress.
    
    Returns:
        Tuple of (successful groups count, successful users count, failed chats log)
    """
    global broadcasting
    
    success_groups = 0
    success_users = 0
    failed_log = ""
    all_chats = groups + users
    total_chats = len(all_chats)
    
    for index, chat_id in enumerate(all_chats, start=1):
        # Check if broadcast was stopped
        if not broadcasting:
            await status_message.edit_text(
                status_message.lang["gcast_stopped"].format(success_groups, success_users)
            )
            break
        
        # Update progress every 50 chats
        if index % 50 == 0:
            try:
                await status_message.edit_text(
                    f"📤 Broadcasting...\n\n"
                    f"Progress: {index}/{total_chats}\n"
                    f"✅ Groups: {success_groups}\n"
                    f"✅ Users: {success_users}"
                )
            except:
                pass
        
        # Attempt to send message
        try:
            # Check if it's a channel (not a group) - skip channels
            if chat_id in groups:
                try:
                    chat = await app.get_chat(chat_id)
                    # Skip channels - only send to supergroups (groups)
                    if chat.type == enums.ChatType.CHANNEL:
                        failed_log += f"{chat_id} - Skipped (channel, not a group)\n"
                        continue
                except:
                    pass  # If can't get chat info, try to send anyway
            
            await app.send_message(chat_id, text)
            
            # Track success
            if chat_id in groups:
                success_groups += 1
            else:
                success_users += 1
            
            # Anti-flood delay: 300ms between messages (safer than 100ms)
            await asyncio.sleep(0.3)
            
        except errors.FloodWait as fw:
            # Handle flood wait by waiting and continuing (don't stop broadcast)
            try:
                await status_message.edit_text(
                    f"⏳ Flood wait triggered. Waiting {fw.value} seconds...\n\n"
                    f"Progress: {index}/{total_chats}\n"
                    f"Don't worry, broadcast will continue!"
                )
            except:
                pass
            
            await asyncio.sleep(fw.value + 5)
            
            # Retry sending after waiting
            try:
                await app.send_message(chat_id, text)
                if chat_id in groups:
                    success_groups += 1
                else:
                    success_users += 1
            except Exception as retry_ex:
                failed_log += f"{chat_id} - FloodWait retry failed: {retry_ex}\n"
        
        except errors.UserIsBlocked:
            # User blocked the bot - skip silently
            failed_log += f"{chat_id} - User blocked bot\n"
            continue
            
        except errors.ChatWriteForbidden:
            # Bot can't write in this chat - skip
            failed_log += f"{chat_id} - No write permission\n"
            continue
        
        except errors.ChannelPrivate:
            # Bot was removed from channel/group - remove from database
            if chat_id in groups:
                try:
                    await db.rm_chat(chat_id)
                    failed_log += f"{chat_id} - Removed from group (cleaned from database)\n"
                except:
                    failed_log += f"{chat_id} - Channel private (bot not member)\n"
            else:
                failed_log += f"{chat_id} - Channel private\n"
            continue
            
        except errors.PeerIdInvalid:
            # Invalid chat ID - remove from database
            if chat_id in groups:
                try:
                    await db.rm_chat(chat_id)
                    failed_log += f"{chat_id} - Invalid ID (cleaned from database)\n"
                except:
                    failed_log += f"{chat_id} - Invalid chat ID\n"
            else:
                failed_log += f"{chat_id} - Invalid user ID\n"
            continue
            
        except Exception as ex:
            # Log failed send but CONTINUE to next chat
            failed_log += f"{chat_id} - {type(ex).__name__}: {str(ex)}\n"
            continue
    
    return success_groups, success_users, failed_log


async def _send_broadcast_completion(
    message: types.Message,
    status_message: types.Message,
    success_groups: int,
    success_users: int,
    failed_log: str
) -> None:
    """
    Send broadcast completion message with results.
    
    Args:
        message: Original command message.
        status_message: Status message to edit.
        success_groups: Number of successful group sends.
        success_users: Number of successful user sends.
        failed_log: Log of failed sends.
    
    Returns:
        None
    """
    completion_text = message.lang["gcast_end"].format(success_groups, success_users)
    
    # If there were failures, send error file
    if failed_log:
        error_file = "errors.txt"
        with open(error_file, "w") as f:
            f.write(failed_log)
        
        await message.reply_document(
            document=error_file,
            caption=completion_text,
        )
        os.remove(error_file)
    
    await status_message.edit_text(completion_text)
