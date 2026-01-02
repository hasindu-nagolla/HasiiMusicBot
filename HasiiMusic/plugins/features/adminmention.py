# ==============================================================================
# adminmention.py - Admin Mention Plugin
# ==============================================================================
# This plugin allows users to mention all group admins by typing @admin,
# .admin, or /admin followed by a message.
#
# Commands:
# - @admin [message] - Mention all admins with a message
# - .admin [message] - Mention all admins with a message
# - /admin [message] - Mention all admins with a message
#
# Requirements:
# - Bot must have permission to read messages in the group
# ==============================================================================

import re
from pyrogram import filters, types, enums

from HasiiMusic import app


# Pattern to detect admin triggers
TRIGGER_PATTERN = re.compile(r"(?i)(\.|@|\/)admin")


@app.on_message(filters.group & filters.regex(r"(?i)(\.|@|\/)admin"))
async def mention_admins(_, message: types.Message):
    """
    Mention all group admins when someone types @admin, .admin, or /admin
    """
    # Extract the message without the trigger
    message_text = message.text or message.caption or ""
    cleaned_text = TRIGGER_PATTERN.sub("", message_text).strip()

    # Get user info (handle anonymous admins)
    sender = message.from_user
    if sender:
        user_display = f"{sender.first_name}"
        if sender.username:
            user_display += f" (@{sender.username})"
    else:
        # Anonymous admin or channel
        user_display = "ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ"

    # Build formatted reply message
    if cleaned_text:
        reply_msg = (
            f"<blockquote><b><i>\"{cleaned_text}\"</i></b>\n"
            f"ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ: {user_display} 🔔</blockquote>\n\n"
        )
    else:
        reply_msg = (
            f"<blockquote>ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ: {user_display} 🔔</blockquote>\n\n"
        )

    # Get all administrators
    mentions = []
    try:
        async for admin in app.get_chat_members(
            message.chat.id,
            filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            user = admin.user

            # Skip bots and deleted accounts
            if user.is_bot or user.is_deleted:
                continue

            # Skip admins who have "Remain Anonymous" enabled
            # Check privileges - if is_anonymous privilege is True, skip them
            if hasattr(admin, 'privileges') and admin.privileges:
                if getattr(admin.privileges, 'is_anonymous', False):
                    continue

            # Add mention
            if user.username:
                mentions.append(f"@{user.username}")
            else:
                # Use HTML link format to mention users without username
                mentions.append(
                    f"<a href='tg://user?id={user.id}'>{user.first_name}</a>")
    except Exception as e:
        await message.reply_text(
            "<blockquote>❌ Failed to fetch administrators. Make sure the bot has proper permissions.</blockquote>"
        )
        return

    if mentions:
        reply_msg += ", ".join(mentions)
    else:
        reply_msg += "<i>No visible human admins found to mention.</i>"

    # Send the reply
    try:
        await message.reply_text(reply_msg, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(
            "<blockquote>❌ Failed to send admin notification.</blockquote>"
        )
