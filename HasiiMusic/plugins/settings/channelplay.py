# ==============================================================================
# channelplay.py - Channel Play Mode Configuration
# ==============================================================================
# This plugin enables playing music in linked channels instead of the group voice chat.
# Useful for groups with linked channels.
# 
# Commands:
# - /channelplay linked - Enable for linked channel
# - /channelplay <channel_id> - Enable for specific channel
# - /channelplay disable - Disable channel play mode
# 
# Requirements:
# - User must be admin
# - Bot must be admin in the channel
# - For "linked" mode, channel must be linked to the group
# ==============================================================================

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import Message

from HasiiMusic import app, config, db


@app.on_message(filters.command(["channelplay"]) & filters.group & ~app.bl_users)
async def channelplay_command(_, m: Message):
    """Enable or disable channel play mode."""
    # Check if user is admin
    member = await app.get_chat_member(m.chat.id, m.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await m.reply_text("❌ Only admins can use this command.")

    if len(m.command) < 2:
        return await m.reply_text(
            f"Channel Play Settings for {m.chat.title}\n\n"
            "To enable for linked channel:\n"
            "`/channelplay linked`\n\n"
            "To enable for any channel:\n"
            "`/channelplay [channel_id]`\n\n"
            "To disable channel play:\n"
            "`/channelplay disable`"
        )

    query = m.text.split(None, 1)[1].strip()

    # Disable channel play
    if query.lower() == "disable":
        await db.set_cmode(m.chat.id, None)
        return await m.reply_text("✅ Channel play disabled.")

    # Enable for linked channel
    elif query.lower() == "linked":
        chat = await app.get_chat(m.chat.id)
        if chat.linked_chat:
            channel_id = chat.linked_chat.id
            await db.set_cmode(m.chat.id, channel_id)
            return await m.reply_text(
                f"✅ Channel play enabled for: {chat.linked_chat.title}\n"
                f"Channel ID: `{chat.linked_chat.id}`"
            )
        else:
            return await m.reply_text("❌ This chat doesn't have a linked channel.")

    # Enable for specific channel
    else:
        # Handle numeric channel IDs
        if query.lstrip("-").isdigit():
            channel_id = int(query)
        else:
            channel_id = query  # Username or invite link

        try:
            chat = await app.get_chat(channel_id)
        except Exception as e:
            return await m.reply_text(
                f"❌ Failed to get channel.\n\n"
                f"Error: `{type(e).__name__}`\n\n"
                "Make sure you've added the bot as admin in the channel and promoted it as admin.\n\n"
                "For numeric IDs: Use the full ID including `-100` prefix\n"
                "Example: `/channelplay -1001234567890`"
            )

        if chat.type != ChatType.CHANNEL:
            return await m.reply_text("❌ Only channels are supported.")

        # Check if user is owner of the channel
        owner_username = None
        owner_id = None
        try:
            async for user in app.get_chat_members(
                chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if user.status == ChatMemberStatus.OWNER:
                    owner_username = user.user.username or "Unknown"
                    owner_id = user.user.id
                    break
        except Exception as e:
            return await m.reply_text(
                f"❌ Failed to get channel administrators.\n\n"
                f"Error: `{type(e).__name__}`\n\n"
                "Make sure the bot is admin in the channel."
            )

        if not owner_id:
            return await m.reply_text(
                "❌ Could not find channel owner.\n\n"
                "Make sure the bot has permission to view channel admins."
            )

        if owner_id != m.from_user.id:
            return await m.reply_text(
                f"❌ You need to be the owner of channel {chat.title} to connect it with this group.\n\n"
                f"Channel's Owner: @{owner_username}\n\n"
                "Alternatively, you can link your chat's channel and connect with `/channelplay linked`"
            )

        await db.set_cmode(m.chat.id, chat.id)
        return await m.reply_text(
            f"✅ Channel play enabled for: {chat.title}\n"
            f"Channel ID: `{chat.id}`"
        )
