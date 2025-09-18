from pyrogram import Client, filters

# Add your allowed group IDs here
ALLOWED_CHAT_IDS = [
    -1002219005418,  
    -1002447971680, 
    -1003079673697,
]

@Client.on_message(filters.group)
async def auto_leave_unauthorized(client, message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        await client.leave_chat(message.chat.id)
