from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode, ChatMemberStatus

from HasiiMusic import app, db


@app.on_message(filters.command(["vcinfo", "vcmembers"]) & filters.group)
async def vc_info_command(client, message: Message):
    """
    Show information about members currently in the voice chat.
    Displays mute status, volume levels, and screen sharing status.
    """
    chat_id = message.chat.id
    
    # Check if user is admin
    try:
        member = await app.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text(
                "❌ <b>Admin Only!</b>\n<blockquote>Only administrators can use this command.</blockquote>",
                parse_mode=ParseMode.HTML
            )
    except Exception:
        return await message.reply_text(
            "⚠️ <b>Error checking admin status.</b>",
            parse_mode=ParseMode.HTML
        )
    
    try:
        # Get the assistant client for this chat
        assistant = await db.get_assistant(chat_id)
        
        # Get voice chat participants
        try:
            participants = await assistant.get_participants(chat_id)
        except Exception:
            return await message.reply_text(
                "❌ <b>No active voice chat found!</b>\n<blockquote>There is no ongoing voice chat in this group.</blockquote>",
                parse_mode=ParseMode.HTML
            )
        
        if not participants:
            return await message.reply_text(
                "❌ <b>No users found in the voice chat.</b>",
                parse_mode=ParseMode.HTML
            )
        
        # Build the response
        msg_lines = ["🎧 <b>VC Members Info:</b>\n"]
        
        for p in participants:
            try:
                user = await app.get_users(p.user_id)
                name = user.mention if user else f"<code>{p.user_id}</code>"
            except Exception:
                name = f"<code>{p.user_id}</code>"
            
            # Get status indicators
            mute_status = "🔇" if p.muted else "👤"
            screen_status = "🖥️" if getattr(p, "screen_sharing", False) else ""
            volume_level = getattr(p, "volume", "N/A")
            
            # Build the info line
            info = f"{mute_status} {name} | 🎚️ {volume_level}"
            if screen_status:
                info += f" | {screen_status}"
            
            msg_lines.append(f"<blockquote>{info}</blockquote>")
        
        msg_lines.append(f"\n👥 <b>Total:</b> {len(participants)}")
        
        await message.reply_text(
            "\n".join(msg_lines),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        await message.reply_text(
            f"⚠️ <b>Failed to fetch VC info.</b>\n<blockquote>Error: {str(e)}</blockquote>",
            parse_mode=ParseMode.HTML
        )
