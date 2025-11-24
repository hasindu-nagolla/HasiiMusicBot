# ==============================================================================
# pause.py - Pause Playback Command
# ==============================================================================
# This plugin handles pausing the current voice chat playback.
# 
# Commands:
# - /pause - Pause current playback
# 
# Requirements:
# - User must be admin or authorized user
# - Music must be currently playing
# ==============================================================================

from pyrogram import filters, types

from HasiiMusic import tune, app, db, lang
from HasiiMusic.helpers import buttons, can_manage_vc


@app.on_message(filters.command(["pause"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _pause(_, m: types.Message):
    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    if not await db.playing(m.chat.id):
        return await m.reply_text(m.lang["play_already_paused"])

    await tune.pause(m.chat.id)
    await m.reply_text(
        text=m.lang["play_paused"].format(m.from_user.mention),
        reply_markup=buttons.controls(m.chat.id),
    )
