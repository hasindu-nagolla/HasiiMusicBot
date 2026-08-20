"""
# ==============================================================================
# utils.py - Calls Utilities
# ==============================================================================
# This file contains stateless utilities for PyTgCalls integration.
# Features:
# - PyTgCalls error filter for cleaner logs
# - Retry wrappers for Telegram message/photo edits during FloodWaits
# ==============================================================================
"""

import asyncio
import logging
from pyrogram import errors
from pyrogram.types import InputMediaPhoto, Message
from HasiiMusic import app

class PyTgCallsErrorFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # ignore UpdateGroupCall errors
        if 'UpdateGroupCall' in msg:
            return False
        # ignore connection errors after a call ends
        if 'Connection with chat id' in msg and 'not found' in msg:
            return False
        # ignore InvalidStateError from PyTgCalls clear_call
        if 'invalid state' in msg.lower() and 'set_exception' in msg:
            return False
        return True


class CallsUtils:
    def __init__(self, controller):
        self.controller = controller

    async def edit_media_with_retry(self, message: Message, media_obj: InputMediaPhoto, reply_markup):
        #edit media and handle FloodWait
        try:
            return await message.edit_media(media=media_obj, reply_markup=reply_markup)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                return await message.edit_media(media=media_obj, reply_markup=reply_markup)
            except Exception:
                return None
        except errors.MessageNotModified:
            return None
        except Exception:
            return None

    async def send_photo_with_retry(self, chat_id: int, photo, caption: str, reply_markup):
        #Send photo with FloodWait handling.
        try:
            return await app.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
            )
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                return await app.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup,
                )
            except Exception:
                return None
        except Exception:
            return None
