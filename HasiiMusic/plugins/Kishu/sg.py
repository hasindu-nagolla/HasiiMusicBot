import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

from HasiiMusic import userbot as us, app
from HasiiMusic.core.userbot import assistants


@app.on_message(filters.command("history"))
async def sg(client: Client, message: Message):
    if not assistants or 1 not in assistants:
        return await message.reply("❌ No active userbot assistant found!")

    ubot = us.one
    status_msg = await message.reply("👀 Checking...")

    # --- Get target user ---
    try:
        if message.reply_to_message:
            target_user_id = message.reply_to_message.from_user.id
        else:
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                return await status_msg.edit("❌ Usage: `/sg` username / id / reply")
            target_user_id = parts[1]

        user = await client.get_users(target_user_id)
    except Exception:
        return await status_msg.edit("❌ Invalid user. Please reply to a user or provide a valid username/id.")

    # --- Pick sangmata bot ---
    sg_bot = random.choice(["sangmata_bot", "sangmata_beta_bot"])

    try:
        forward_msg = await ubot.send_message(sg_bot, str(user.id))
        await forward_msg.delete()
    except Exception as e:
        return await status_msg.edit(f"❌ Failed to contact `{sg_bot}`\n`{e}`")

    await asyncio.sleep(2)

    # --- Search for bot response ---
    found = False
    async for stalk in ubot.search_messages(sg_bot, limit=5):  # limit for efficiency
        if stalk.text:
            await message.reply(stalk.text)
            found = True
            break

    if not found:
        await message.reply("🤖 No username history found.")

    # --- Cleanup history ---
    try:
        peer = await ubot.resolve_peer(sg_bot)
        await ubot.send(DeleteHistory(peer=peer, max_id=0, revoke=True))
    except Exception:
        pass

    await status_msg.delete()
