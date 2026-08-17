# ==============================================================================
# lang.py - Language Configuration
# ==============================================================================
# Allows group administrators to change the language of the bot.
# ==============================================================================

from pyrogram import filters, types
from pyrogram.enums import ChatType
from HasiiMusic import app, db, lang
from HasiiMusic.core.lang import lang_codes
from HasiiMusic.helpers import can_manage_vc


def get_lang_keyboard():
    """Generate the language selection inline keyboard."""
    keyboard = []
    
    # We create a 2-column layout for aesthetics
    row = []
    for code, name in lang_codes.items():
        row.append(
            types.InlineKeyboardButton(
                text=name,
                callback_data=f"set_lang_{code}"
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
            
    if row:
        keyboard.append(row)
        
    return types.InlineKeyboardMarkup(keyboard)


@app.on_message(filters.command(["lang", "language"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def set_lang_command(_, message: types.Message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(message.lang["lang_group_only"])

    keyboard = get_lang_keyboard()
    
    await message.reply_text(
        text=message.lang["lang_menu_title"],
        reply_markup=keyboard,
        quote=False
    )


@app.on_callback_query(filters.regex(r"^set_lang_") & ~app.bl_users)
@lang.language()
async def set_lang_callback(client, query: types.CallbackQuery):
    try:
        lang_code = query.data.split("_")[2]
    except IndexError:
        return await query.answer("Invalid callback data.", show_alert=True)

    if lang_code not in lang_codes:
        return await query.answer("Language not supported.", show_alert=True)
        
    if query.message.chat.type == ChatType.PRIVATE:
        return await query.answer(query.lang["lang_group_only"], show_alert=True)
        
    # We must authorize the user since it's a callback query
    # Check if the user is an admin or the owner
    try:
        member = await client.get_chat_member(query.message.chat.id, query.from_user.id)
    except Exception:
        return await query.answer("Could not verify permissions.", show_alert=True)
        
    if not (member.privileges and member.privileges.can_manage_video_chats) and query.from_user.id not in app.sudoers and member.status != getattr(types, "ChatMemberStatus", type("Mock", (object,), {"OWNER": "owner"})).OWNER and str(member.status) not in ["ChatMemberStatus.OWNER", "ChatMemberStatus.ADMINISTRATOR"]:
        # Allow checking for any admin status if privileges check failed
        if "ADMINISTRATOR" not in str(member.status) and "OWNER" not in str(member.status):
            return await query.answer(query.lang["lang_admin_only"], show_alert=True)

    # Save to database
    await db.set_lang(query.message.chat.id, lang_code)

    # Inform user
    try:
        lang_name = lang_codes[lang_code]
        # Re-fetch new translation dict for immediate effect in this callback if needed
        new_lang_dict = (await lang.get_lang(query.message.chat.id))
        
        await query.message.edit_text(
            text=new_lang_dict["lang_success"].format(lang_name),
            reply_markup=None
        )
        await query.answer("Language changed successfully!", show_alert=False)
    except Exception as e:
        await query.answer("Failed to update message.", show_alert=True)
