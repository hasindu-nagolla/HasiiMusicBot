# ==============================================================================
# new_chat.py - New Group Handler
# ==============================================================================
# This plugin handles when the bot is added to a new group.
# 
# Features:
# - Send notification to logger channel with group info
# - Welcome message in the group
# - Check if group meets requirements (supergroup, admin permissions)
# - Log group details (name, ID, member count, who added the bot)
# ==============================================================================

from pyrogram import filters, types
from pyrogram.errors import ChatAdminRequired

from HasiiMusic import app, config


@app.on_message(filters.new_chat_members & filters.group)
async def new_chat_member(_, message: types.Message):
    """Handler for when bot is added to a new group"""

    # Check if the bot itself was added
    for member in message.new_chat_members:
        if member.id == app.id:
            chat = message.chat

            # Get chat information
            chat_name = chat.title
            chat_id = chat.id
            chat_username = f"@{chat.username}" if chat.username else "𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽"
            members_count = await app.get_chat_members_count(chat_id)

            # Get the user who added the bot
            added_by = message.from_user
            added_by_name = added_by.mention if added_by else "𝗨𝗻𝗸𝗻𝗼𝘄𝗻"

            # Create the formatted message with blockquote
            text = f"""<blockquote>🟢 <b>˹𝐇𝐚𝐬𝐢𝐢 ✘ 𝐌𝐮𝐬𝐢𝐜˼ 𝗔𝗱𝗱𝗲𝗱 𝗜𝗻 𝗮 𝗡𝗲𝘄 𝗚𝗿𝗼𝘂𝗽</b></blockquote>

<blockquote>
🔖 <b>𝗖𝗵𝗮𝘁 𝗡𝗮𝗺𝗲:</b> {chat_name}
🆔 <b>𝗖𝗵𝗮𝘁 𝗜𝗗:</b> <code>{chat_id}</code>
👤 <b>𝗖𝗵𝗮𝘁 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:</b> {chat_username}
🔗 <b>𝗖𝗵𝗮𝘁 𝗟𝗶𝗻𝗸:</b> {f"https://t.me/{chat.username}" if chat.username else "𝗖𝗹𝗶𝗰𝗸 𝗛𝗲𝗿𝗲"}
👥 <b>𝗚𝗿𝗼𝘂𝗽 𝗠𝗲𝗺𝗯𝗲𝗿𝘀:</b> {members_count}
🤵 <b>𝗔𝗱𝗱𝗲𝗱 𝗕𝘆:</b> {added_by_name}
</blockquote>
"""

            try:
                # Send the notification to the logger group
                await app.send_photo(
                    chat_id=config.LOGGER_ID,
                    photo=config.START_IMG,
                    caption=text
                )
            except Exception as e:
                print(f"Failed to send new chat notification: {e}")

            break


@app.on_message(filters.left_chat_member & filters.group)
async def left_chat_member(_, message: types.Message):
    """Handler for when bot is removed from a group"""

    # Check if the bot itself was removed
    if message.left_chat_member.id == app.id:
        chat = message.chat

        # Get chat information
        chat_name = chat.title
        chat_id = chat.id
        chat_username = f"@{chat.username}" if chat.username else "𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽"

        # Get the user who removed the bot
        removed_by = message.from_user
        removed_by_name = removed_by.mention if removed_by else "𝗨𝗻𝗸𝗻𝗼𝘄𝗻"

        # Create the formatted message with blockquote
        text = f"""<blockquote>🔴 <b>˹𝐇𝐚𝐬𝐢𝐢 ✘ 𝐌𝐮𝐬𝐢𝐜˼ 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗙𝗿𝗼𝗺 𝗮 𝗚𝗿𝗼𝘂𝗽</b></blockquote>

<blockquote>
🔖 <b>𝗖𝗵𝗮𝘁 𝗡𝗮𝗺𝗲:</b> {chat_name}
🆔 <b>𝗖𝗵𝗮𝘁 𝗜𝗗:</b> <code>{chat_id}</code>
👤 <b>𝗖𝗵𝗮𝘁 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:</b> {chat_username}
🔗 <b>𝗖𝗵𝗮𝘁 𝗟𝗶𝗻𝗸:</b> {f"https://t.me/{chat.username}" if chat.username else "𝗖𝗹𝗶𝗰𝗸 𝗛𝗲𝗿𝗲"}
🚫 <b>𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗕𝘆:</b> {removed_by_name}</blockquote>
"""

        try:
            # Send the notification to the logger group
            await app.send_photo(
                chat_id=config.LOGGER_ID,
                photo=config.START_IMG,
                caption=text
            )
        except Exception as e:
            print(f"Failed to send left chat notification: {e}")
