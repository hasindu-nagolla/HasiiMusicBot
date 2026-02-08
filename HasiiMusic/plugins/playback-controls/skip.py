# ==============================================================================
# skip.py - Skip Track Command
# ==============================================================================
# This plugin handles skipping to the next track in the queue.
#
# Commands:
# - /skip - Skip current track and play next
# - /next - Same as /skip
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing
# ==============================================================================

import asyncio
from pyrogram import filters, types

from HasiiMusic import tune, app, db, lang
from HasiiMusic.helpers import can_manage_vc


@app.on_message(filters.command(["skip", "next"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _skip(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    await tune.play_next(m.chat.id)
    sent_msg = await m.reply_text(m.lang["play_skipped"].format(m.from_user.mention))
    
    # Auto-delete after 5 seconds
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass
