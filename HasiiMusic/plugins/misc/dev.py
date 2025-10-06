from pyrogram import filters
from HasiiMusic import app

@app.on_message(filters.command("sayyara") & filters.user(8172401675))  # Replace with your user ID
async def leave_group(client, message):
    await message.reply("Leaving group now.")
    await client.leave_chat(-1002178211234)  # Replace with your group ID
