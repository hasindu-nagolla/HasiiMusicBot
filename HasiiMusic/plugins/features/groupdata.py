from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode, ChatMemberStatus, ChatMembersFilter
from pyrogram.types import Message

from HasiiMusic import app


@app.on_message(filters.command(["groupdata", "chatinfo", "groupinfo"]) & filters.group)
async def group_data_handler(client: Client, message: Message):
    """Display comprehensive information about the current group"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    chat = message.chat
    chat_id = chat.id
    
    try:
        # Get chat information
        chat_info = await client.get_chat(chat_id)
        
        # Count members by type
        total_members = 0
        admin_count = 0
        bot_count = 0
        banned_count = 0
        deleted_count = 0
        premium_count = 0
        
        try:
            total_members = await client.get_chat_members_count(chat_id)
            
            # Count admins
            async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
                admin_count += 1
            
            # Count bots
            async for _ in client.get_chat_members(chat_id, filter=ChatMembersFilter.BOTS):
                bot_count += 1
                
            # Count banned users
            try:
                async for _ in client.get_chat_members(chat_id, filter=ChatMembersFilter.BANNED):
                    banned_count += 1
            except Exception:
                pass
            
            # Iterate through recent members to count deleted accounts and premium users
            try:
                member_sample = 0
                async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.SEARCH, limit=200):
                    member_sample += 1
                    if member.user.is_deleted:
                        deleted_count += 1
                    if member.user.is_premium:
                        premium_count += 1
            except Exception:
                pass
                
        except Exception:
            pass
        
        # Build information text
        info_lines = []
        info_lines.append("<b>📊 GROUP INFORMATION</b>\n")
        
        # Basic info
        info_lines.append(f"<b>📌 ɴᴀᴍᴇ:</b> {chat_info.title}")
        info_lines.append(f"<b>🆔 ɪᴅ:</b> <code>{chat_id}</code>")
        
        if chat_info.username:
            info_lines.append(f"<b>🔗 ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{chat_info.username}")
        
        # Chat type
        chat_type_str = "ɢʀᴏᴜᴘ" if chat.type == ChatType.GROUP else "ꜱᴜᴘᴇʀɢʀᴏᴜᴘ"
        info_lines.append(f"<b>📂 ᴛʏᴘᴇ:</b> {chat_type_str}")
        
        # Member statistics
        info_lines.append(f"\n<b>👥 ᴍᴇᴍʙᴇʀꜱ:</b> {total_members}")
        info_lines.append(f"<b>👮 ᴀᴅᴍɪɴꜱ:</b> {admin_count}")
        info_lines.append(f"<b>🤖 ʙᴏᴛꜱ:</b> {bot_count}")
        
        if banned_count > 0:
            info_lines.append(f"<b>🚫 ʙᴀɴɴᴇᴅ:</b> {banned_count}")
        
        if deleted_count > 0:
            info_lines.append(f"<b>👻 ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ:</b> {deleted_count}")
            
        if premium_count > 0:
            info_lines.append(f"<b>⭐ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ:</b> {premium_count}")
        
        # Description if available
        if chat_info.description:
            desc = chat_info.description
            if len(desc) > 100:
                desc = desc[:100] + "..."
            info_lines.append(f"\n<b>📝 ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ:</b>\n{desc}")
        
        # Linked chat if available
        if chat_info.linked_chat:
            info_lines.append(f"\n<b>🔗 ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ:</b> {chat_info.linked_chat.title}")
            info_lines.append(f"<b>🆔 ᴄʜᴀɴɴᴇʟ ɪᴅ:</b> <code>{chat_info.linked_chat.id}</code>")
        
        # Invite link if available
        if hasattr(chat_info, 'invite_link') and chat_info.invite_link:
            info_lines.append(f"\n<b>🔗 ɪɴᴠɪᴛᴇ ʟɪɴᴋ:</b> {chat_info.invite_link}")
        
        # Check user's admin status
        try:
            user_member = await client.get_chat_member(chat_id, message.from_user.id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                info_lines.append(f"\n<b>🔐 ʏᴏᴜʀ ʀᴏʟᴇ:</b> {'ᴏᴡɴᴇʀ' if user_member.status == ChatMemberStatus.OWNER else 'ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀ'}")
        except Exception:
            pass
        
        # Combine all info
        response = "<blockquote>" + "\n".join(info_lines) + "</blockquote>"
        
        await message.reply_text(
            response,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await message.reply_text(
            f"<blockquote>❌ <b>ᴇʀʀᴏʀ ɢᴇᴛᴛɪɴɢ ɢʀᴏᴜᴘ ᴅᴀᴛᴀ:</b>\n<code>{str(e)}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
