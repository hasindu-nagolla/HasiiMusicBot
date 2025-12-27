# ==============================================================================
# loop.py - Loop Mode Command
# ==============================================================================
# This plugin handles loop mode management.
#
# Commands:
# - /loop - Cycle through loop modes (off -> single -> queue -> off)
# - /loop off - Disable loop
# - /loop single - Loop current track
# - /loop queue - Loop entire queue
#
# Requirements:
# - User must be admin or authorized user
# ==============================================================================

from pyrogram import filters, types

from HasiiMusic import app, db, lang
from HasiiMusic.helpers import can_manage_vc


@app.on_message(filters.command(["loop"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _loop(_, m: types.Message):
    current_loop = await db.get_loop(m.chat.id)
    
    # Check if user specified a mode
    if len(m.command) > 1:
        mode_arg = m.command[1].lower()
        if mode_arg in ["off", "0", "disable"]:
            new_loop = 0
            text = "➡️ Loop mode **disabled**"
        elif mode_arg in ["single", "1", "one"]:
            new_loop = 1
            text = "🔂 Loop mode set to **Single Track**"
        elif mode_arg in ["queue", "all", "10"]:
            new_loop = 10
            text = "🔁 Loop mode set to **Queue**"
        else:
            return await m.reply_text(
                "**Usage:**\n"
                "• `/loop` - Cycle through modes\n"
                "• `/loop off` - Disable loop\n"
                "• `/loop single` - Loop current track\n"
                "• `/loop queue` - Loop entire queue"
            )
    else:
        # Cycle through modes
        if current_loop == 0:
            new_loop = 1
            text = "🔂 Loop mode set to **Single Track**"
        elif current_loop == 1:
            new_loop = 10
            text = "🔁 Loop mode set to **Queue**"
        else:
            new_loop = 0
            text = "➡️ Loop mode **disabled**"
    
    await db.set_loop(m.chat.id, new_loop)
    await m.reply_text(text)
