# ==============================================================================
# stop.py - Stop Playback Command
# ==============================================================================
# This plugin handles stopping voice chat playback and clearing the queue.
#
# Commands:
# - /stop - Stop playback and clear queue
# - /end - Same as /stop
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing
# ==============================================================================

import asyncio
from pyrogram import filters, types

from HasiiMusic import tune, app, db, lang
from HasiiMusic.helpers import can_manage_vc


@app.on_message(filters.command(["end", "stop"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _stop(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if len(m.command) > 1:
        return
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    await tune.stop(m.chat.id)
    sent_msg = await m.reply_text(m.lang["play_stopped"].format(m.from_user.mention))
    
    # Auto-delete after 5 seconds
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass
