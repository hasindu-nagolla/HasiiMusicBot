# ==============================================================================
# _admins.py - Admin Permission Decorators
# ==============================================================================
# This file contains decorator functions that check user permissions.
# These decorators are used to protect commands that require admin rights.
#
# Available decorators:
# - @admin_check: Requires user to be group admin or sudo user
# - @can_manage_vc: Requires permission to manage voice chats (or be authorized)
# ==============================================================================

from functools import wraps

from pyrogram import StopPropagation, enums, types

from HasiiMusic import app, db


def admin_check(func):
    """
    Decorator to check if user is an admin in the chat.
    
    - Allows sudo users (owner) to bypass admin check
    - Checks if user is in the admin list for the chat
    - Returns error message if user is not admin
    
    Usage:
        @admin_check
        async def my_admin_command(_, message):
            # Only admins can execute this
            pass
    """
    @wraps(func)
    async def wrapper(_, update: types.Message | types.CallbackQuery, *args, **kwargs):
        # Helper function to send reply (works for messages and callbacks)
        async def reply(text):
            if isinstance(update, types.Message):
                return await update.reply_text(text)
            else:
                return await update.answer(text, show_alert=True)

        # Get chat ID and user ID from update
        chat_id = (
            update.chat.id
            if isinstance(update, types.Message)
            else update.message.chat.id
        )
        user_id = update.from_user.id
        
        # Get list of admins from database (cached)
        admins = await db.get_admins(chat_id)

        # Sudo users (bot owner) can bypass admin check
        if user_id in app.sudoers:
            return await func(_, update, *args, **kwargs)

        # Check if user is admin
        if user_id not in admins:
            return await reply(update.lang["user_no_perms"])

        # User is admin, allow execution
        return await func(_, update, *args, **kwargs)

    return wrapper


def can_manage_vc(func):
    """
    Decorator to check if user can manage voice chats.
    
    Allows:
    - Sudo users (bot owner)
    - Authorized users (added via /auth command)
    - Group admins with voice chat management permission
    
    Usage:
        @can_manage_vc
        async def my_vc_command(_, message):
            # Only users with VC permissions can execute this
            pass
    """
    @wraps(func)
    async def wrapper(_, update: types.Message | types.CallbackQuery, *args, **kwargs):
        # Get chat ID and user ID
        chat_id = (
            update.chat.id
            if isinstance(update, types.Message)
            else update.message.chat.id
        )
        user_id = update.from_user.id

        # Sudo users can always manage VC
        if user_id in app.sudoers:
            return await func(_, update, *args, **kwargs)

        # Check if user is in authorized users list
        if await db.is_auth(chat_id, user_id):
            return await func(_, update, *args, **kwargs)

        admins = await db.get_admins(chat_id)
        if user_id in admins:
            return await func(_, update, *args, **kwargs)

        if isinstance(update, types.Message):
            return await update.reply_text(update.lang["user_no_perms"])
        else:
            return await update.answer(update.lang["user_no_perms"], show_alert=True)

    return wrapper


async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in await db.get_admins(chat_id):
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        ]
    except:
        raise StopPropagation


async def reload_admins(chat_id: int) -> list[int]:
    try:
        admins = [
            admin
            async for admin in app.get_chat_members(
                chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            )
            if not admin.user.is_bot
        ]
        return [admin.user.id for admin in admins]
    except:
        return []
