# ==============================================================================
# _dataclass.py - Data Classes for Media and Tracks
# ==============================================================================
# This file defines data structures used throughout the bot:
# - Media: Represents Telegram audio/video files
# - Track: Represents YouTube tracks
# 
# These dataclasses make it easy to pass media information between functions
# while maintaining type safety and clear structure.
# ==============================================================================

from dataclasses import dataclass


@dataclass
class Media:
    id: str
    duration: str
    duration_sec: int
    file_path: str
    message_id: int
    title: str
    url: str
    time: int = 0
    user: str = None
    video: bool = False
    is_live: bool = False


@dataclass
class Track:
    id: str
    channel_name: str
    duration: str
    duration_sec: int
    title: str
    url: str
    file_path: str = None
    message_id: int = 0
    time: int = 0
    thumbnail: str = None
    user: str = None
    view_count: str = None
    video: bool = False
    is_live: bool = False
