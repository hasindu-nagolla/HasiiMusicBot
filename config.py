# ==============================================================================
# config.py - Bot Configuration Manager
# ==============================================================================
# This file loads all configuration settings from environment variables (.env file).
# 
# What it does:
# - Reads settings from .env file (API keys, bot token, database URL, etc.)
# - Validates that all required settings are present
# - Provides default values for optional settings
# - Converts string values to appropriate types (int, bool, list)
# 
# Important: Never commit your .env file to git! It contains sensitive data.
# Use sample.env as a template to create your own .env file.
# ==============================================================================

"""
Configuration module for HasiiMusicBot.

This module loads and validates all environment variables required for the bot to function.
It provides a centralized Config class that manages all configuration settings.
"""

from os import getenv
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file (create one from sample.env)
load_dotenv()


class Config:
    """
    Configuration class for managing bot settings.
    
    All settings are loaded from environment variables with sensible defaults where applicable.
    Required variables are validated on initialization through the check() method.
    """
    
    def __init__(self):
        """Initialize configuration by loading all environment variables."""
        
        # ============ TELEGRAM API CREDENTIALS ============
        # Get these from https://my.telegram.org
        self.API_ID: int = int(getenv("API_ID", "0"))  # Telegram API ID (numeric)
        self.API_HASH: str = getenv("API_HASH", "")    # Telegram API Hash (hexadecimal)
        
        # ============ BOT CONFIGURATION ============
        self.BOT_TOKEN: str = getenv("BOT_TOKEN", "")        # Bot token from @BotFather
        self.LOGGER_ID: int = int(getenv("LOGGER_ID", "0"))  # Group/channel ID for logs (must be negative)
        self.OWNER_ID: int = int(getenv("OWNER_ID", "0"))    # Your user ID (get from @userinfobot)
        
        # ============ DATABASE CONFIGURATION ============
        self.MONGO_URL: str = getenv("MONGO_DB_URI", "")  # MongoDB connection URL (mongodb+srv://...)
        
        # ============ MUSIC BOT LIMITS ============
        # Convert minutes to seconds for duration limit
        self.DURATION_LIMIT: int = int(getenv("DURATION_LIMIT", "150")) * 60  # Max song duration (default: 150 min)
        self.QUEUE_LIMIT: int = int(getenv("QUEUE_LIMIT", "30"))             # Max songs in queue (default: 30)
        self.PLAYLIST_LIMIT: int = int(getenv("PLAYLIST_LIMIT", "20"))       # Max songs from playlist (default: 20)
        
        # ============ ASSISTANT/USERBOT SESSIONS ============
        # Pyrogram session strings - get from @StringFatherBot
        # You can have up to 3 assistants for handling multiple groups
        self.SESSION1: str = getenv("STRING_SESSION", "")  # Primary assistant (required)
        self.SESSION2: str = getenv("SESSION2", "")        # Secondary assistant (optional)
        self.SESSION3: str = getenv("SESSION3", "")        # Tertiary assistant (optional)
        
        # ============ SUPPORT LINKS ============
        self.SUPPORT_CHANNEL: str = getenv("SUPPORT_CHANNEL", "https://t.me/TheInfinityAI")
        self.SUPPORT_CHAT: str = getenv("SUPPORT_CHAT", "https://t.me/Hasindu_Lakshan")
        
        # ============ EXCLUDED CHATS ============
        # Parse comma-separated chat IDs that assistants should never leave
        self.EXCLUDED_CHATS: List[int] = self._parse_excluded_chats()
        
        # ============ FEATURE FLAGS ============
        self.AUTO_END: bool = self._str_to_bool(getenv("AUTO_END", "False"))      # Auto-end stream when queue is empty
        self.AUTO_LEAVE: bool = self._str_to_bool(getenv("AUTO_LEAVE", "False"))  # Auto-leave inactive chats
        self.VIDEO_PLAY: bool = self._str_to_bool(getenv("VIDEO_PLAY", "True"))   # Enable video playback
        
        # ============ YOUTUBE COOKIES ============
        # Parse space-separated cookie URLs for age-restricted content
        self.COOKIES_URL: List[str] = self._parse_cookies()
        
        # ============ IMAGE URLS ============
        # URLs for various bot images
        self.DEFAULT_THUMB: str = getenv(
            "DEFAULT_THUMB",
            "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"  # Default thumbnail
        )
        self.PING_IMG: str = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")    # Ping command image
        self.START_IMG: str = getenv("START_IMG", "https://files.catbox.moe/und0yt.jpg")  # Start command image
    
    def _parse_excluded_chats(self) -> List[int]:
        """
        Parse excluded chat IDs from comma-separated string.
        
        Returns:
            List[int]: List of chat IDs to exclude from auto-leave.
        """
        excluded = getenv("EXCLUDED_CHATS", "")
        if not excluded:
            return []
        
        chat_ids = []
        for chat_id in excluded.split(","):
            chat_id = chat_id.strip()
            if chat_id.lstrip('-').isdigit():
                chat_ids.append(int(chat_id))
        return chat_ids
    
    def _parse_cookies(self) -> List[str]:
        """
        Parse YouTube cookie URLs from space-separated string.
        
        Returns:
            List[str]: List of valid cookie URLs.
        """
        cookie_str = getenv("COOKIE_URL", "")
        if not cookie_str:
            return []
        
        return [
            url.strip()
            for url in cookie_str.split()
            if url.strip() and "batbin.me" in url
        ]
    
    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """
        Convert string to boolean value.
        
        Args:
            value: String representation of boolean.
            
        Returns:
            bool: Converted boolean value.
        """
        return value.lower() in ("true", "1", "yes", "y", "on")
    
    def check(self) -> None:
        """
        Validate that all required environment variables are set.
        
        Raises:
            SystemExit: If any required variables are missing.
        """
        required_vars = {
            "API_ID": self.API_ID,
            "API_HASH": self.API_HASH,
            "BOT_TOKEN": self.BOT_TOKEN,
            "MONGO_DB_URI": self.MONGO_URL,
            "LOGGER_ID": self.LOGGER_ID,
            "OWNER_ID": self.OWNER_ID,
            "STRING_SESSION": self.SESSION1,
        }
        
        missing = [
            name for name, value in required_vars.items()
            if not value or (isinstance(value, int) and value == 0)
        ]
        
        if missing:
            raise SystemExit(
                f"❌ Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file and ensure all required variables are set."
            )
