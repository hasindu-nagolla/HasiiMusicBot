# ==============================================================================
# leave.py - Force Leave Commands (Sudo Only)
# ==============================================================================
# This plugin allows sudo users to make the bot and assistants leave chats.
#
# Commands:
# - /leave - Make bot and assistant leave the current chat
# - /leaveall - Make all assistants leave all inactive chats
#
# Only sudo users can use these commands.
# ==============================================================================

import asyncio
from pyrogram import filters, types, errors, enums

from HasiiMusic import app, db, lang, logger, userbot, config


@app.on_message(filters.command(["leave"]) & app.sudo_filter)
@lang.language()
async def _leave(_, m: types.Message):
    """
    Command handler for /leave
    Makes both bot and assistant leave the current chat.
    """
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    chat_id = m.chat.id
    chat_name = m.chat.title or "this chat"

    # Send confirmation message
    sent = await m.reply_text(
        f"<blockquote><b>👋 Leaving Chat</b></blockquote>\n\n"
        f"<blockquote>Bot and assistant are leaving <b>{chat_name}</b>...</blockquote>"
    )

    # Try to make assistant leave if it's in the chat
    try:
        client = await db.get_client(chat_id)
        try:
            await client.leave_chat(chat_id)
        except errors.UserNotParticipant:
            # Assistant is not in the chat, skip
            pass
        except Exception as e:
            # Log any other errors but continue with bot leaving
            pass
    except Exception:
        # If getting client fails, just continue with bot leaving
        pass

    # Make bot leave the chat
    try:
        await app.leave_chat(chat_id)
    except Exception as e:
        # If bot can't leave, inform the sudo user
        await sent.edit_text(
            f"<blockquote><b>❌ Error</b></blockquote>\n\n"
            f"<blockquote>Failed to leave chat: {str(e)}</blockquote>"
        )


@app.on_message(filters.command(["leaveall"]) & app.sudo_filter)
@lang.language()
async def _leaveall(_, m: types.Message):
    """
    Command handler for /leaveall
    Makes all assistants leave all inactive groups (not in active calls).
    """
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(
        f"<blockquote><b>🔄 Processing...</b></blockquote>\n\n"
        f"<blockquote>Making assistants leave all inactive groups...</blockquote>"
    )
    
    total_left = 0
    
    for ub in userbot.clients:
        left = 0
        try:
            async for dialog in ub.get_dialogs():
                chat_id = dialog.chat.id
                
                # Skip logger and excluded chats
                excluded = [app.logger] + config.EXCLUDED_CHATS
                if chat_id in excluded:
                    continue
                
                # Only leave groups and supergroups
                if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    # Skip if currently in an active call
                    if chat_id in db.active_calls:
                        continue
                    
                    try:
                        await ub.leave_chat(chat_id)
                        left += 1
                        total_left += 1
                        await asyncio.sleep(1)  # Rate limit
                    except Exception as e:
                        logger.debug(f"Failed to leave {chat_id}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in leaveall for assistant {ub.me.username if hasattr(ub, 'me') and ub.me else 'Unknown'}: {e}")
            continue
    
    await sent.edit_text(
        f"<blockquote><b>✅ Cleanup Complete</b></blockquote>\n\n"
        f"<blockquote>Assistants left <b>{total_left}</b> inactive groups.</blockquote>"
    )
