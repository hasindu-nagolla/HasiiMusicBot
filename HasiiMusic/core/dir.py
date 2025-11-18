# ==============================================================================
# dir.py - Directory Management
# ==============================================================================
# This file ensures that required directories exist for the bot to store:
# - cache: Temporary cache files
# - downloads: Downloaded audio/video files from Telegram or YouTube
# These directories are created automatically on startup if they don't exist.
# ==============================================================================

from pathlib import Path

from HasiiMusic import logger


def ensure_dirs():
    """
    Create necessary directories if they don't exist.
    
    Creates:
    - cache/: For temporary cache files
    - downloads/: For downloaded media files
    """
    # List of required directories
    for dir in ["cache", "downloads"]:
        Path(dir).mkdir(parents=True, exist_ok=True)  # Create directory (and parents if needed)
    logger.info("📁 Cache directories updated.")
