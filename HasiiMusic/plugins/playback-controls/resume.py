# ==============================================================================
# resume.py - Resume Playback Command
# ==============================================================================
# This plugin handles resuming paused voice chat playback.
#
# Commands:
# - /resume - Resume paused playback
#
# Requirements:
# - User must be admin or authorized user
# - Music must be currently paused
# ==============================================================================

import logging
from pyrogram import filters, types
from pyrogram.errors import ChatSendPlainForbidden

from HasiiMusic import tune, app, db, lang
from HasiiMusic.helpers import buttons, can_manage_vc

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["resume"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _resume(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if not await db.get_call(m.chat.id):
        try:
            return await m.reply_text(m.lang["not_playing"])
        except ChatSendPlainForbidden:
            return

    if await db.playing(m.chat.id):
        try:
            return await m.reply_text(m.lang["play_not_paused"])
        except ChatSendPlainForbidden:
            return

    await tune.resume(m.chat.id)
    try:
        await m.reply_text(
            text=m.lang["play_resumed"].format(m.from_user.mention),
            reply_markup=buttons.controls(m.chat.id),
        )
    except ChatSendPlainForbidden:
        logger.warning("Cannot send plain text in media-only chat")
