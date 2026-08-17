# ==============================================================================
# blacklist.py - Blacklisting
# ==============================================================================
# Sudo commands to block toxic users or spammy chats from using the bot entirely.
# ==============================================================================

from pyrogram import filters, types
from HasiiMusic import app, db, lang


@app.on_message(filters.command(["blacklistchat"]) & app.sudo_filter)
@lang.language()
async def _blacklist_chat(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if len(m.command) < 2:
        return await m.reply_text(
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/blacklistchat [chat_id]</code></blockquote>"
        )

    try:
        chat_id = int(m.command[1])
        chat = await app.get_chat(chat_id)
    except ValueError:
        return await m.reply_text(m.lang["bl_invalid_chat"])
    except Exception:
        return await m.reply_text(m.lang["bl_chat_not_found"])

    if chat_id in db.blacklisted:
        return await m.reply_text(
            f"<blockquote>⚠️ {chat.title} is already blacklisted</blockquote>"
        )

    await db.add_blacklist(chat_id)
    await m.reply_text(
        f"<blockquote><u><b>✅ ᴄʜᴀᴛ ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ</b></u>\n\n"
        f"<b>ᴄʜᴀᴛ:</b> {chat.title}\n"
        f"<b>ɪᴅ:</b> <code>{chat_id}</code></blockquote>"
    )


@app.on_message(filters.command(["whitelistchat", "unblacklistchat"]) & app.sudo_filter)
@lang.language()
async def _whitelist_chat(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if len(m.command) < 2:
        return await m.reply_text(
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/whitelistchat [chat_id]</code></blockquote>"
        )

    try:
        chat_id = int(m.command[1])
        try:
            chat = await app.get_chat(chat_id)
            chat_name = chat.title
        except:
            chat_name = f"Chat {chat_id}"
    except ValueError:
        return await m.reply_text(m.lang["bl_invalid_chat"])

    if chat_id not in db.blacklisted:
        return await m.reply_text(
            f"<blockquote>⚠️ {chat_name} is not blacklisted</blockquote>"
        )

    await db.del_blacklist(chat_id)
    await m.reply_text(
        f"<blockquote><u><b>✅ ᴄʜᴀᴛ ᴡʜɪᴛᴇʟɪꜱᴛᴇᴅ</b></u>\n\n"
        f"<b>ᴄʜᴀᴛ:</b> {chat_name}\n"
        f"<b>ɪᴅ:</b> <code>{chat_id}</code></blockquote>"
    )


@app.on_message(filters.command(["blacklistedchat", "blchats"]) & app.sudo_filter)
@lang.language()
async def _blacklisted_chats(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(m.lang["bl_fetching_chats"])
    
    blacklisted = await db.get_blacklisted(chat=True)
    
    # Filter only chats (negative IDs)
    chats_list = [chat_id for chat_id in blacklisted if chat_id < 0]
    
    if not chats_list:
        return await sent.edit_text(m.lang["bl_no_chats"])
    
    text = "<u><b>🚫 ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴄʜᴀᴛꜱ:</b></u>\n<blockquote>"
    
    for chat_id in chats_list:
        try:
            chat = await app.get_chat(chat_id)
            text += f"\n- {chat.title} ({chat_id})"
        except:
            text += f"\n- Unknown Chat ({chat_id})"
    
    text += "\n\n</blockquote>"
    await sent.edit_text(text)


# ============== USER BLACKLIST COMMANDS ==============

@app.on_message(filters.command(["block"]) & app.sudo_filter)
@lang.language()
async def _block_user(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # Extract user from command or reply
    user_id = None
    
    if m.reply_to_message and m.reply_to_message.from_user:
        user_id = m.reply_to_message.from_user.id
        user_mention = m.reply_to_message.from_user.mention
    elif len(m.command) > 1:
        try:
            user_id = int(m.command[1])
            user = await app.get_users(user_id)
            user_mention = user.mention
        except ValueError:
            return await m.reply_text(m.lang["bl_invalid_user"])
        except Exception:
            return await m.reply_text(m.lang["bl_user_not_found"])
    else:
        return await m.reply_text(
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/block [user_id]</code>\n"
            "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ</blockquote>"
        )
    
    # Don't allow blocking sudo users
    if user_id in app.sudoers:
        return await m.reply_text(m.lang["bl_sudo_error"])
    
    if user_id in app.bl_users:
        return await m.reply_text(
            f"<blockquote>⚠️ {user_mention} is already blocked</blockquote>"
        )

    app.bl_users.add(user_id)
    await db.add_blacklist(user_id)
    await m.reply_text(
        f"<blockquote><u><b>✅ ᴜꜱᴇʀ ʙʟᴏᴄᴋᴇᴅ</b></u>\n\n"
        f"<b>ᴜꜱᴇʀ:</b> {user_mention}\n"
        f"<b>ɪᴅ:</b> <code>{user_id}</code></blockquote>"
    )


@app.on_message(filters.command(["unblock"]) & app.sudo_filter)
@lang.language()
async def _unblock_user(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # Extract user from command or reply
    user_id = None
    
    if m.reply_to_message and m.reply_to_message.from_user:
        user_id = m.reply_to_message.from_user.id
        user_mention = m.reply_to_message.from_user.mention
    elif len(m.command) > 1:
        try:
            user_id = int(m.command[1])
            user = await app.get_users(user_id)
            user_mention = user.mention
        except ValueError:
            return await m.reply_text(m.lang["bl_invalid_user"])
        except Exception:
            user_mention = f"User {user_id}"
    else:
        return await m.reply_text(
            "<blockquote><b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/unblock [user_id]</code>\n"
            "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ</blockquote>"
        )
    
    if user_id not in app.bl_users:
        return await m.reply_text(
            f"<blockquote>⚠️ {user_mention} is not blocked</blockquote>"
        )

    app.bl_users.discard(user_id)
    await db.del_blacklist(user_id)
    await m.reply_text(
        f"<blockquote><u><b>✅ ᴜꜱᴇʀ ᴜɴʙʟᴏᴄᴋᴇᴅ</b></u>\n\n"
        f"<b>ᴜꜱᴇʀ:</b> {user_mention}\n"
        f"<b>ɪᴅ:</b> <code>{user_id}</code></blockquote>"
    )


@app.on_message(filters.command(["blockedusers", "blusers"]) & app.sudo_filter)
@lang.language()
async def _blocked_users(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(m.lang["bl_fetching_users"])
    
    blacklisted = await db.get_blacklisted()
    
    if not blacklisted:
        return await sent.edit_text(m.lang["bl_no_users"])
    
    text = "<u><b>🚫 ʙʟᴏᴄᴋᴇᴅ ᴜꜱᴇʀꜱ:</b></u>\n<blockquote>"
    
    for user_id in blacklisted:
        try:
            user = await app.get_users(user_id)
            text += f"\n- {user.mention} ({user_id})"
        except:
            text += f"\n- Deleted Account ({user_id})"
    
    text += "\n\n</blockquote>"
    await sent.edit_text(text)
