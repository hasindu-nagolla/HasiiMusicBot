"""
# ==============================================================================
# __init__.py - Calls Facade
# ==============================================================================
# This file serves as the main entry point for PyTgCalls integration.
# Features:
# - Exposes the public API for the TgCall class
# - Initializes and delegates to modular sub-components
# ==============================================================================
"""

import asyncio
import logging
from pytgcalls import PyTgCalls
from pyrogram.types import Message
from HasiiMusic.helpers import Media, Track

from .utils import CallsUtils, PyTgCallsErrorFilter
from .manager import CallsManager
from .player import CallPlayer
from .controls import CallControls
from .queue import CallQueue

logging.getLogger('pyrogram.dispatcher').addFilter(PyTgCallsErrorFilter())

class TgCall(PyTgCalls):
    def __init__(self):
        super().__init__()
        
        # Shared state
        self.clients = []
        self._chat_locks = {}
        self._session_gen = {}
        self._track_index = {}
        self._pending_transitions = set()

        # Components
        self._utils = CallsUtils(self)
        self._manager = CallsManager(self)
        self._player = CallPlayer(self)
        self._controls = CallControls(self)
        self._queue = CallQueue(self)

    def get_lock(self, chat_id: int) -> asyncio.Lock:
        if chat_id not in self._chat_locks:
            self._chat_locks[chat_id] = asyncio.Lock()
        return self._chat_locks[chat_id]

    async def boot(self) -> None:
        return await self._manager.boot()

    async def ping(self) -> float:
        return await self._manager.ping()

    async def pause(self, chat_id: int) -> bool:
        return await self._controls.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        return await self._controls.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        return await self._controls.stop(chat_id)

    async def seek_stream(self, chat_id: int, seconds: int) -> bool:
        return await self._controls.seek_stream(chat_id, seconds)

    async def play_media(
        self,
        chat_id: int,
        message: Message | None,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        return await self._player.play_media(chat_id, message, media, seek_time)

    async def replay(self, chat_id: int) -> None:
        return await self._queue.replay(chat_id)

    async def play_next(self, chat_id: int, expected_index: int = None) -> None:
        return await self._queue.play_next(chat_id, expected_index)
