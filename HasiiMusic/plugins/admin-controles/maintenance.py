# ==============================================================================
# maintenance.py - Maintenance Mode (Sudo Only)
# ==============================================================================
# This plugin allows bot owner/sudo users to enable maintenance mode.
# When enabled, only sudo users can use the bot - regular users are blocked.
#
# Commands:
# - /maintenance [enable|disable] - Toggle maintenance mode
# - /maintenance - Check current status
#
# Only sudo users can manage maintenance mode.
# ==============================================================================

from pyrogram import filters, types

from HasiiMusic import app, db, lang


@app.on_message(filters.command(["maintenance"]) & app.sudo_filter)
@lang.language()
async def _maintenance(_, m: types.Message):
    """Toggle or check maintenance mode status."""
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # If no argument, show current status
    if len(m.command) < 2:
        status = await db.get_maintenance()
        status_text = "🔴 ᴇɴᴀʙʟᴇᴅ" if status else "🟢 ᴅɪꜱᴀʙʟᴇᴅ"
        
        await m.reply_text(
            f"<blockquote><u><b>🔧 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ꜱᴛᴀᴛᴜꜱ</b></u>\n\n"
            f"<b>ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ:</b> {status_text}\n\n"
            f"<b>ᴜꜱᴀɢᴇ:</b>\n"
            f"<code>/maintenance enable</code> - Enable mode\n"
            f"<code>/maintenance disable</code> - Disable mode</blockquote>"
        )
        return
    
    mode = m.command[1].lower()
    
    if mode in ["enable", "on", "1", "true"]:
        await db.set_maintenance(True)
        await m.reply_text(
            "<blockquote><u><b>🔴 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ</b></u>\n\n"
            "ᴏɴʟʏ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ɴᴏᴡ.\n"
            "ʀᴇɢᴜʟᴀʀ ᴜꜱᴇʀꜱ ᴡɪʟʟ ꜱᴇᴇ ᴀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴇꜱꜱᴀɢᴇ.</blockquote>"
        )
        
    elif mode in ["disable", "off", "0", "false"]:
        await db.set_maintenance(False)
        await m.reply_text(
            "<blockquote><u><b>🟢 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ</b></u>\n\n"
            "ᴛʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴀʟʟ ᴜꜱᴇʀꜱ.</blockquote>"
        )
        
    else:
        await m.reply_text(
            "<blockquote>❌ <b>ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ</b>\n\n"
            "<b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/maintenance enable</code>\n"
            "<code>/maintenance disable</code></blockquote>"
        )
