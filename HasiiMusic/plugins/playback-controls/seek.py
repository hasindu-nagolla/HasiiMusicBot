# ==============================================================================
# seek.py - Seek to Timestamp Command
# ==============================================================================
# This plugin allows seeking to a specific timestamp in the current track.
#
# Commands:
# - /seek <seconds> - Seek forward to timestamp
# - /seekback <seconds> - Seek backward to timestamp
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing (not paused)
# - Track must have a known duration (not live streams)
# - Minimum seek: 10 seconds
# ==============================================================================

from pyrogram import filters, types

from HasiiMusic import tune, app, db, lang, queue
from HasiiMusic.helpers import can_manage_vc


@app.on_message(filters.command(["seek", "seekback"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _seek(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))

    try:
        to_seek = int(m.command[1])
    except ValueError:
        return await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))
    if to_seek < 10:
        return await m.reply_text(m.lang["play_seek_min"])

    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    if not await db.playing(m.chat.id):
        return await m.reply_text(m.lang["play_already_paused"])

    media = queue.get_current(m.chat.id)
    if not media.duration_sec:
        return await m.reply_text(m.lang["play_seek_no_dur"])

    sent = await m.reply_text(m.lang["play_seeking"])
    
    current_time = getattr(media, 'time', 0)
    if m.command[0] == "seekback":
        stype = m.lang["backward"]
        start_from = max(1, current_time - to_seek)
    else:
        stype = m.lang["forward"]
        start_from = min(current_time + to_seek, media.duration_sec - 5)

    # Use the new seek_stream method
    success = await tune.seek_stream(m.chat.id, int(start_from))
    
    if success:
        await sent.edit_text(
            m.lang["play_seeked"].format(stype, start_from, m.from_user.mention)
        )
    else:
        await sent.edit_text("❌ Failed to seek!")
