# ==============================================================================
# _preload.py - Background Track Preloading Manager
# ==============================================================================
# This module handles downloading the next track in the background while
# the current track is playing to ensure seamless transitions.
#
# Features:
# - Background download of next track
# - Automatic cancellation of outdated preload tasks
# - Prevents redundant downloads
# - Non-blocking async operations
# ==============================================================================

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger("HasiiMusic")


class PreloadManager:
    """
    Manages background preloading of upcoming tracks in queue.
    
    This ensures smooth transitions between songs by downloading
    the next track before the current one finishes.
    """

    def __init__(self):
        """Initialize the preload manager."""
        self._tasks: Dict[int, asyncio.Task] = {}
        self._preloaded: Dict[int, str] = {}  # chat_id -> media_id

    async def preload_next(self, chat_id: int, media) -> None:
        """
        Start preloading the next track for a chat.
        
        Args:
            chat_id: The chat ID to preload for
            media: The Media/Track object to preload
        """
        # Cancel any existing preload task for this chat
        await self.cancel_preload(chat_id)

        # Check if already preloaded
        if self._preloaded.get(chat_id) == media.id:
            logger.debug(f"Track {media.id} already preloaded for chat {chat_id}")
            return

        # Start new preload task
        task = asyncio.create_task(self._preload_task(chat_id, media))
        self._tasks[chat_id] = task

    async def _preload_task(self, chat_id: int, media) -> None:
        """
        Background task to preload a track.
        
        Args:
            chat_id: The chat ID to preload for
            media: The Media/Track object to preload
        """
        try:
            # Import here to avoid circular dependency
            from HasiiMusic import yt

            logger.debug(f"Starting preload for chat {chat_id}: {media.title}")
            
            # Download the track
            if not media.file_path:
                media.file_path = await yt.download(media.id)
                self._preloaded[chat_id] = media.id
                logger.debug(f"Preload complete for chat {chat_id}: {media.title}")
            else:
                logger.debug(f"Track already has file_path for chat {chat_id}: {media.title}")
                self._preloaded[chat_id] = media.id
                
        except asyncio.CancelledError:
            logger.debug(f"Preload cancelled for chat {chat_id}")
            raise
        except Exception as e:
            logger.error(f"Preload error for chat {chat_id}: {e}")
        finally:
            # Clean up task reference
            self._tasks.pop(chat_id, None)

    async def cancel_preload(self, chat_id: int) -> None:
        """
        Cancel any active preload task for a chat.
        
        Args:
            chat_id: The chat ID to cancel preload for
        """
        task = self._tasks.get(chat_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.debug(f"Cancelled preload for chat {chat_id}")
        
        # Clear preloaded cache
        self._preloaded.pop(chat_id, None)
        self._tasks.pop(chat_id, None)

    def is_preloaded(self, chat_id: int, media_id: str) -> bool:
        """
        Check if a specific track is preloaded for a chat.
        
        Args:
            chat_id: The chat ID to check
            media_id: The media ID to check
            
        Returns:
            bool: True if the track is preloaded
        """
        return self._preloaded.get(chat_id) == media_id

    def clear(self, chat_id: int) -> None:
        """
        Clear preload cache for a chat (non-async version).
        
        Args:
            chat_id: The chat ID to clear
        """
        self._preloaded.pop(chat_id, None)
        self._tasks.pop(chat_id, None)

    async def start_preload(self, chat_id: int, count: int = 2) -> None:
        """
        Start preloading multiple upcoming tracks from queue.
        
        Args:
            chat_id: The chat ID to preload for
            count: Number of tracks to preload (default: 2)
        """
        try:
            # Import here to avoid circular dependency
            from HasiiMusic import queue
            
            # Get full queue and preload upcoming tracks (skip first one - that's current)
            all_tracks = queue.get_queue(chat_id)
            if len(all_tracks) > 1:
                # Preload next 'count' tracks
                upcoming = all_tracks[1:min(1 + count, len(all_tracks))]
                for media in upcoming:
                    if not media.file_path:
                        await self.preload_next(chat_id, media)
                        
        except Exception as e:
            logger.debug(f"Error in start_preload for {chat_id}: {e}")

