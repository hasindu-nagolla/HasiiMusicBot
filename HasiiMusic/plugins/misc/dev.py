from pyrogram import filters
from HasiiMusic import app

@app.on_message(filters.command("leavegroup") & filters.user(REPLACE_WITH_YOUR_USER_ID))
async def leave_group(client, message):
    await message.reply("Leaving group now.")
    await client.leave_chat(REPLACE_WITH_YOUR_GROUP_ID)
