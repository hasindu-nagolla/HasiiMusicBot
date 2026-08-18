# ==============================================================================
# _preload.py - Track Preloading Logic
# ==============================================================================
# Internal logic for managing the background downloading of upcoming tracks.
# ==============================================================================

import asyncio
import logging
from typing import Dict, Set

logger = logging.getLogger("HasiiMusic")


class PreloadManager:
    """
    Manages background preloading of upcoming tracks in queue.
    
    This ensures smooth transitions between songs by downloading
    the next track before the current one finishes.
    """

    def __init__(self):
        # Track active preload tasks by chat and media id:
        # {chat_id: {media_id: task}}
        self._tasks: Dict[int, Dict[str, asyncio.Task]] = {}
        # Track successfully preloaded media ids by chat:
        # {chat_id: {media_id, ...}}
        self._preloaded: Dict[int, Set[str]] = {}

    async def preload_next(self, chat_id: int, media) -> None:
        media_id = getattr(media, "id", None)
        if not media_id:
            return

        # Initialize per-chat stores
        if chat_id not in self._tasks:
            self._tasks[chat_id] = {}
        if chat_id not in self._preloaded:
            self._preloaded[chat_id] = set()

        # Skip if already preloaded
        if media_id in self._preloaded[chat_id]:
            logger.debug(f"Track {media_id} already preloaded for chat {chat_id}")
            return

        # Skip if already actively preloading
        existing = self._tasks[chat_id].get(media_id)
        if existing and not existing.done():
            return

        # Start new preload task
        task = asyncio.create_task(self._preload_task(chat_id, media))
        self._tasks[chat_id][media_id] = task

    async def _preload_task(self, chat_id: int, media) -> None:
        try:
            # Import here to avoid circular dependency
            from HasiiMusic import yt

            logger.debug(f"Starting preload for chat {chat_id}: {media.title}")
            
            # Download the track
            if not media.file_path:
                import re
                if not re.fullmatch(r"[A-Za-z0-9_-]{11}", media.id) or not getattr(media, "thumbnail", None):
                    try:
                        resolved = await yt.search(media.id, 0)
                        if resolved:
                            media.id = resolved.id
                            if resolved.thumbnail:
                                media.thumbnail = resolved.thumbnail
                            if resolved.duration_sec:
                                media.duration_sec = resolved.duration_sec
                                media.duration = resolved.duration
                    except Exception:
                        pass
                media.file_path = await yt.download(
                    media.id,
                    video=getattr(media, "video", False),
                )
                if media.file_path:
                    self._preloaded.setdefault(chat_id, set()).add(media.id)
                logger.debug(f"Preload complete for chat {chat_id}: {media.title}")
            else:
                logger.debug(f"Track already has file_path for chat {chat_id}: {media.title}")
                self._preloaded.setdefault(chat_id, set()).add(media.id)
                
        except asyncio.CancelledError:
            logger.debug(f"Preload cancelled for chat {chat_id}")
            raise
        except Exception as e:
            logger.error(f"Preload error for chat {chat_id}: {e}")
        finally:
            # Clean up task reference for this specific media id
            media_tasks = self._tasks.get(chat_id)
            if media_tasks:
                media_tasks.pop(getattr(media, "id", None), None)
                if not media_tasks:
                    self._tasks.pop(chat_id, None)

    async def cancel_preload(self, chat_id: int) -> None:
        media_tasks = self._tasks.get(chat_id, {})
        if media_tasks:
            active = [task for task in media_tasks.values() if not task.done()]
            for task in active:
                task.cancel()
            if active:
                await asyncio.gather(*active, return_exceptions=True)
            logger.debug(f"Cancelled preload for chat {chat_id}")
        
        # Clear preloaded cache
        self._preloaded.pop(chat_id, None)
        self._tasks.pop(chat_id, None)

    def is_preloaded(self, chat_id: int, media_id: str) -> bool:
        return media_id in self._preloaded.get(chat_id, set())

    def clear(self, chat_id: int) -> None:
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

