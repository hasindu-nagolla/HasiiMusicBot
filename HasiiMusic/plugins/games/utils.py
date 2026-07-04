import asyncio
from pyrogram.errors import MessageNotModified, FloodWait

async def safe_edit(message, text=None, reply_markup=None):
    try:
        if text:
            await message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.edit_reply_markup(reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            if text:
                await message.edit_text(text, reply_markup=reply_markup)
            else:
                await message.edit_reply_markup(reply_markup=reply_markup)
        except:
            pass
