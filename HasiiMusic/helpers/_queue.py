# ==============================================================================
# _queue.py - Music Queue Manager
# ==============================================================================
# This file manages the music queue for each chat.
# - Each chat has its own separate queue
# - Queues are stored in memory (lost on restart)
# - Supports adding, removing, and retrieving songs from the queue
# - Uses deque (double-ended queue) for efficient operations
# ==============================================================================

from collections import defaultdict, deque
from typing import Union

from ._dataclass import Media, Track

# MediaItem can be either a Media or Track object
MediaItem = Union[Media, Track]


class Queue:
    def __init__(self):
        """Initialize the queue manager with empty queues for all chats."""
        # Dictionary mapping chat_id to its queue (deque of Media/Track items)
        # defaultdict automatically creates a new deque for new chat_ids
        self.queues: dict[int, deque[MediaItem]] = defaultdict(deque)

    def add(self, chat_id: int, item: MediaItem) -> int:
        """Add a song to the end of the queue and return its position."""
        self.queues[chat_id].append(item)  # Add to end of queue
        return len(self.queues[chat_id]) - 1  # Return position (0-based index)

    def check_item(self, chat_id: int, item_id: str) -> tuple[int, MediaItem | None]:
        """Check if an item with the given ID exists in the queue."""
        pos, track = next(
            (
                (i, track)
                for i, track in enumerate(list(self.queues[chat_id]))
                if track.id == item_id
            ),
            (-1, None),
        )
        return pos, track

    def force_add(
        self, chat_id: int, item: MediaItem, remove: int | bool = False
    ) -> None:
        """Replace the currently playing item with a new one."""
        self.remove_current(chat_id)
        self.queues[chat_id].appendleft(item)
        if remove:
            self.queues[chat_id].rotate(-remove)
            self.queues[chat_id].popleft()
            self.queues[chat_id].rotate(remove)

    def get_current(self, chat_id: int) -> MediaItem | None:
        """Return the currently playing item (first in queue), if any."""
        return self.queues[chat_id][0] if self.queues[chat_id] else None

    def get_next(self, chat_id: int, check: bool = False) -> MediaItem | None:
        """Remove current item and return the next one, or None if empty."""
        if not self.queues[chat_id]:
            return None
        if check:
            return self.queues[chat_id][1] if len(self.queues[chat_id]) > 1 else None

        self.queues[chat_id].popleft()
        return self.queues[chat_id][0] if self.queues[chat_id] else None

    def get_queue(self, chat_id: int) -> list[MediaItem]:
        """Return the full queue including the currently playing item."""
        return list(self.queues[chat_id])

    def remove_current(self, chat_id: int) -> None:
        """Remove the currently playing item only (if exists)."""
        if self.queues[chat_id]:
            self.queues[chat_id].popleft()

    def clear(self, chat_id: int) -> None:
        """Clear the entire queue."""
        self.queues[chat_id].clear()
