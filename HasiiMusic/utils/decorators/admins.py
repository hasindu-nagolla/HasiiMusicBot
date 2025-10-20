from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from HasiiMusic import app
from HasiiMusic.misc import SUDOERS, db
from HasiiMusic.utils.database import (
    get_authuser_names,
    get_cmode,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_maintenance,
    is_nonadmin_chat,
    is_skipmode,
)
from config import SUPPORT_CHAT, adminlist, confirmer
from strings import get_string
from ..formatters import int_to_alpha


def AdminRightsCheck(mystic):
    async def wrapper(client, message):
        # Maintenance check
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\n"
                    f"ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴜᴘᴅᴀᴛᴇs.",
                    disable_web_page_preview=True,
                )

        # Try deleting user command
        try:
            await message.delete()
        except Exception:
            pass

        # Load language
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
        except Exception:
            _ = get_string("en")

        # Anonymous check
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        "ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]
                ]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        # Channel‑play mode
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                await app.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id

        if not await is_active_chat(chat_id):
            return await message.reply_text(_["general_5"])

        # Admin enforcement
        is_non_admin = await is_nonadmin_chat(message.chat.id)
        if not is_non_admin and message.from_user.id not in SUDOERS:
            try:
                member = await app.get_chat_member(message.chat.id, message.from_user.id)
                # Check by privileges OR status
                if not (
                    getattr(member, "privileges", None)
                    or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                ):
                    return await message.reply_text(_["admin_14"])
            except Exception:
                return await message.reply_text(_["admin_14"])

        # Hand control back to command
        return await mystic(client, message, _, chat_id)

    return wrapper


def AdminActual(mystic):
    async def wrapper(client, message):
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\n"
                    f"ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴜᴘᴅᴀᴛᴇs.",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
        except Exception:
            _ = get_string("en")

        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if message.from_user.id not in SUDOERS:
            try:
                member = await app.get_chat_member(message.chat.id, message.from_user.id)
                if not (
                    getattr(member, "privileges", None)
                    or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                ):
                    return await message.reply_text(_["general_4"])
            except Exception:
                return await message.reply_text(_["general_4"])

        return await mystic(client, message, _)

    return wrapper


def ActualAdminCB(mystic):
    async def wrapper(client, CallbackQuery):
        if await is_maintenance() is False:
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.",
                    show_alert=True,
                )

        try:
            language = await get_lang(CallbackQuery.message.chat.id)
            _ = get_string(language)
        except Exception:
            _ = get_string("en")

        if CallbackQuery.message.chat.type == ChatType.PRIVATE:
            return await mystic(client, CallbackQuery, _)

        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            try:
                member = await app.get_chat_member(
                    CallbackQuery.message.chat.id,
                    CallbackQuery.from_user.id,
                )
                if not (
                    getattr(member, "privileges", None)
                    or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                ):
                    return await CallbackQuery.answer(_["general_4"], show_alert=True)
            except Exception:
                return await CallbackQuery.answer(_["general_4"], show_alert=True)

        return await mystic(client, CallbackQuery, _)

    return wrapper
