# ==============================================================================
# blacklist.py - User/Chat Blacklist Commands (Sudo Only)
# ==============================================================================
# This plugin manages the bot blacklist to block abusive users/chats.
# Blacklisted entities cannot use the bot.
#
# Commands:
# - /blacklist <user_id|chat_id|@username> - Add to blacklist
# - /unblacklist <user_id|chat_id|@username> - Remove from blacklist
# - /whitelist <user_id|chat_id|@username> - Same as /unblacklist
# - /blacklistlist - Show all blacklisted users and chats
#
# Only sudo users can manage the blacklist.
# ==============================================================================

from pyrogram import filters, types

from HasiiMusic import app, db, lang


@app.on_message(filters.command(["blacklistlist", "listblacklist"]) & app.sudo_filter)
@lang.language()
async def _blacklist_list(_, m: types.Message):
    sent = await m.reply_text("📋 Fetching blacklist...")
    
    blacklisted = await db.get_blacklisted()
    
    if not blacklisted:
        return await sent.edit_text("✅ No users or chats are blacklisted.")
    
    users_list = ""
    chats_list = ""
    
    for entity_id in blacklisted:
        try:
            chat = await app.get_chat(entity_id)
            if entity_id > 0:  # User
                users_list += f"\n- {chat.first_name}" + (f" {chat.last_name}" if chat.last_name else "") + f" ({entity_id})"
            else:  # Group/Channel
                chats_list += f"\n- {chat.title} ({entity_id})"
        except:
            # Deleted or inaccessible
            if entity_id > 0:
                users_list += f"\n- Deleted Account ({entity_id})"
            else:
                chats_list += f"\n- Unknown Chat ({entity_id})"
    
    text = "<u><b>🚫 ʙʟᴀᴄᴋʟɪꜱᴛᴇᴅ ᴇɴᴛɪᴛɪᴇꜱ:</b></u>\n"
    
    if users_list:
        text += f"<blockquote><b>ᴜꜱᴇʀꜱ:</b>{users_list}\n\n</blockquote>"
    
    if chats_list:
        text += f"<blockquote><b>ᴄʜᴀᴛꜱ:</b>{chats_list}\n\n</blockquote>"
    
    await sent.edit_text(text)


@app.on_message(filters.command(["blacklist", "unblacklist", "whitelist"]) & app.sudo_filter)
@lang.language()
async def _blacklist(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["bl_usage"].format(m.command[0]))

    try:
        chat_id = m.command[1]
        if not str(chat_id).startswith("@"):
            chat_id = int(chat_id)
        else:
            chat_id = (await app.get_chat(chat_id)).id
    except:
        return await m.reply_text(m.lang["bl_invalid"])

    if m.command[0] == "blacklist":
        if chat_id in db.blacklisted or chat_id in app.bl_users:
            return await m.reply_text(m.lang["bl_already"])
        if not str(chat_id).startswith("-"):
            app.bl_users.add(chat_id)
        await db.add_blacklist(chat_id)
        await m.reply_text(m.lang["bl_added"])
    else:
        if chat_id not in db.blacklisted and chat_id not in app.bl_users:
            return await m.reply_text(m.lang["bl_not"])
        if not str(chat_id).startswith("-"):
            app.bl_users.discard(chat_id)
        await db.del_blacklist(chat_id)
        await m.reply_text(m.lang["bl_removed"])
