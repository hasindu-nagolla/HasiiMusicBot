from pyrogram import filters
from HasiiMusic import app
import config

@app.on_message(filters.command("play") & filters.user(config.LEAVE_GROUP_USER_ID))
async def leave_group(client, message):
    await message.reply("Leaving group now.")
    await client.leave_chat(config.LEAVE_GROUP_CHAT_ID)
