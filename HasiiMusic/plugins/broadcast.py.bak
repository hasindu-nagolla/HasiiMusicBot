import os
import asyncio

from pyrogram import errors, filters, types

from HasiiMusic import app, db, lang


broadcasting = False

@app.on_message(filters.command(["broadcast"]) & app.sudoers)
@lang.language()
async def _broadcast(_, message: types.Message):
    global broadcasting
    
    # Extract the broadcast message from command
    if len(message.command) < 2:
        return await message.reply_text(message.lang["gcast_usage"])

    if broadcasting:
        return await message.reply_text(message.lang["gcast_active"])

    # Parse flags and extract actual message
    parts = message.text.split(None, 1)[1].split()
    flags = [part for part in parts if part.startswith('-')]
    message_parts = [part for part in parts if not part.startswith('-')]
    
    if not message_parts:
        return await message.reply_text(message.lang["gcast_usage"])
    
    broadcast_text = ' '.join(message_parts)
    
    count, ucount = 0, 0
    chats, groups, users = [], [], []
    sent = await message.reply_text(message.lang["gcast_start"])

    if "-nochat" not in flags:
        groups.extend(await db.get_chats())
    if "-user" in flags:
        users.extend(await db.get_users())

    chats.extend(groups + users)
    broadcasting = True

    # Log to logger group
    await (await app.send_message(
        chat_id=app.logger, 
        text=message.lang["gcast_log"].format(
            message.from_user.id,
            message.from_user.mention,
            message.text,
        )
    )).pin(disable_notification=False)
    await asyncio.sleep(5)

    failed = ""
    for chat in chats:
        if not broadcasting:
            await sent.edit_text(message.lang["gcast_stopped"].format(count, ucount))
            break

        try:
            # Send as direct message from bot
            await app.send_message(chat, broadcast_text)
            if chat in groups:
                count += 1
            else:
                ucount += 1
            await asyncio.sleep(0.1)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 30)
            # Retry after flood wait
            try:
                await app.send_message(chat, broadcast_text)
                if chat in groups:
                    count += 1
                else:
                    ucount += 1
            except Exception as retry_ex:
                failed += f"{chat} - {retry_ex}\n"
        except Exception as ex:
            failed += f"{chat} - {ex}\n"
            continue

    text = message.lang["gcast_end"].format(count, ucount)
    if failed:
        with open("errors.txt", "w") as f:
            f.write(failed)
        await message.reply_document(
            document="errors.txt",
            caption=text,
        )
        os.remove("errors.txt")
    broadcasting = False
    await sent.edit_text(text)


@app.on_message(filters.command(["stop_gcast", "stop_broadcast"]) & app.sudoers)
@lang.language()
async def _stop_gcast(_, message: types.Message):
    global broadcasting
    if not broadcasting:
        return await message.reply_text(message.lang["gcast_inactive"])

    broadcasting = False
    await (await app.send_message(
        chat_id=app.logger,
        text=message.lang["gcast_stop_log"].format(
            message.from_user.id,
            message.from_user.mention
        )

    )).pin(disable_notification=False)
    await message.reply_text(message.lang["gcast_stop"])

