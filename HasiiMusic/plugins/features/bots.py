from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter

from HasiiMusic import app


@app.on_message(filters.command("bots") & filters.group)
async def list_bots(client, message: Message):
    """List all bots in the current group"""
    
    try:
        bot_list = []
        bot_count = 0
        
        # Send initial message
        status_msg = await message.reply_text("🔍 **Scanning for bots...**")
        
        # Iterate through all members and filter bots
        async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.BOTS):
            bot_count += 1
            bot_username = f"@{member.user.username}" if member.user.username else "No Username"
            bot_list.append(f"{bot_count}. [{member.user.first_name}](tg://user?id={member.user.id}) - {bot_username}")
        
        if bot_count == 0:
            await status_msg.edit_text("❌ **No bots found in this group.**")
            return
        
        # Format the response
        response = f"🤖 **Bots in {message.chat.title}**\n\n"
        response += "\n".join(bot_list)
        response += f"\n\n📊 **Total Bots:** {bot_count}"
        
        await status_msg.edit_text(response, disable_web_page_preview=True)
        
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")
