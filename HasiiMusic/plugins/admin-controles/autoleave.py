# ==============================================================================
# autoleave.py - Auto Leave Command
# ==============================================================================
# This plugin allows sudo users to enable/disable auto-leave feature.
# When enabled, assistant will leave voice chat after 5 minutes if no users
# are listening (only assistant is in the VC).
# ==============================================================================

from pyrogram import filters
from pyrogram.types import Message

from HasiiMusic import app, db


@app.on_message(
    filters.command(["autoleave"])
    & filters.group
    & ~app.bl_users
)
async def autoleave_command(_, m: Message) -> None:
    """Handle /autoleave enable or /autoleave disable command."""
    
    # Check if user is sudo user
    if m.from_user.id not in app.sudoers:
        return await m.reply_text(
            "❌ ᴏɴʟʏ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
        )
    
    # Check if subcommand is provided
    if len(m.command) < 2:
        current_status = await db.get_autoleave(m.chat.id)
        status_text = "ᴇɴᴀʙʟᴇᴅ" if current_status else "ᴅɪꜱᴀʙʟᴇᴅ"
        return await m.reply_text(
            f"<blockquote>🔧 ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ ꜱᴛᴀᴛᴜꜱ: {status_text}</blockquote>\n\n"
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "• `/autoleave enable` - ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ\n"
            "• `/autoleave disable` - ᴅɪꜱᴀʙʟᴇ ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ</blockquote>\n\n"
            "<blockquote><i>ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴡɪʟʟ ʟᴇᴀᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀꜰᴛᴇʀ 5 ᴍɪɴᴜᴛᴇꜱ "
            "ɪꜰ ɴᴏ ᴜꜱᴇʀꜱ ᴀʀᴇ ʟɪꜱᴛᴇɴɪɴɢ.</i></blockquote>"
        )
    
    subcommand = m.command[1].lower()
    
    if subcommand == "enable":
        await db.set_autoleave(m.chat.id, True)
        await m.reply_text(
            "✅ <blockquote>ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ ᴇɴᴀʙʟᴇᴅ!</blockquote>\n\n"
            "<blockquote>ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴡɪʟʟ ʟᴇᴀᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀꜰᴛᴇʀ <b>5 ᴍɪɴᴜᴛᴇꜱ</b> "
            "ɪꜰ ɴᴏ ᴜꜱᴇʀꜱ ᴀʀᴇ ʟɪꜱᴛᴇɴɪɴɢ.</blockquote>"
        )
    elif subcommand == "disable":
        await db.set_autoleave(m.chat.id, False)
        await m.reply_text(
            "✅ <blockquote>ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ ᴅɪꜱᴀʙʟᴇᴅ!</blockquote>\n\n"
            "<blockquote>ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴡɪʟʟ ꜱᴛᴀʏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇᴠᴇɴ ᴡʜᴇɴ ɴᴏ ᴏɴᴇ ɪꜱ ʟɪꜱᴛᴇɴɪɴɢ.</blockquote>"
        )
    else:
        await m.reply_text(
            "❌ <blockquote>ɪɴᴠᴀʟɪᴅ ꜱᴜʙᴄᴏᴍᴍᴀɴᴅ!</blockquote>\n\n"
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "• `/autoleave enable`\n"
            "• `/autoleave disable`</blockquote>"
        )
