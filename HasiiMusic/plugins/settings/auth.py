# ==============================================================================
# auth.py - Authorization Management Commands
# ==============================================================================
# This plugin manages authorized users who can control music playback.
# Authorized users can use playback commands even if they're not admins.
# 
# Commands:
# - /auth <user> - Grant playback control permissions to user
# - /unauth <user> - Revoke playback control permissions from user
# - /admincache - Reload admin list cache for current chat
# - /reload - Same as /admincache
# 
# Only group admins can add/remove authorized users.
# ==============================================================================

import time

from pyrogram import filters, types

from HasiiMusic import app, db, lang
from HasiiMusic.helpers import admin_check, is_admin, utils


@app.on_message(filters.command(["auth", "unauth"]) & filters.group & ~app.bl_users)
@lang.language()
@admin_check
async def _auth(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(m.lang["user_not_found"])

    if m.command[0] == "auth":
        if await is_admin(m.chat.id, user.id):
            return await m.reply_text(m.lang["auth_is_admin"])

        await db.add_auth(m.chat.id, user.id)
        await m.reply_text(m.lang["auth_added"].format(user.mention))
    else:
        await db.rm_auth(m.chat.id, user.id)
        await m.reply_text(m.lang["auth_removed"].format(user.mention))


rel_hist = {}


@app.on_message(filters.command(["admincache", "reload"]) & filters.group & ~app.bl_users)
@lang.language()
async def _admincache(_, m: types.Message):
    if m.from_user.id in rel_hist:
        if time.time() < rel_hist[m.from_user.id]:
            return await m.reply_text(m.lang["admin_cache_wait"])

    rel_hist[m.from_user.id] = time.time() + 600
    sent = await m.reply_text(m.lang["admin_cache_reloading"])
    await db.get_admins(m.chat.id, reload=True)
    await sent.edit_text(m.lang["admin_cache_reloaded"])
