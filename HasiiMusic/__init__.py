"""
HasiiMusicBot - Advanced Telegram Music Bot

This is the main initialization module that sets up logging, configuration,
and all core components required for the bot to function.
"""

import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List

# Configure logging
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)

# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)

logger = logging.getLogger("HasiiMusic")

# Version
__version__ = "3.0.1"

# Load configuration
from config import Config

config = Config()
config.check()

# Global task list for background tasks
tasks: List = []
boot: float = time.time()

# Initialize bot client
from HasiiMusic.core.bot import Bot
app = Bot()

# Ensure required directories exist
from HasiiMusic.core.dir import ensure_dirs
ensure_dirs()

# Initialize userbot/assistant clients
from HasiiMusic.core.userbot import Userbot
userbot = Userbot()

# Initialize database connection
from HasiiMusic.core.mongo import MongoDB
db = MongoDB()

# Initialize language system
from HasiiMusic.core.lang import Language
lang = Language()

# Initialize Telegram and YouTube utilities
from HasiiMusic.core.telegram import Telegram
from HasiiMusic.core.youtube import YouTube
tg = Telegram()
yt = YouTube()

# Initialize queue manager
from HasiiMusic.helpers import Queue
queue = Queue()

# Initialize call handler
from HasiiMusic.core.calls import TgCall
anon = TgCall()


async def stop() -> None:
    """
    Gracefully shutdown the bot and all its components.
    
    This function:
    - Cancels all running background tasks
    - Closes bot and userbot connections
    - Closes database connection
    - Logs shutdown completion
    """
    logger.info("🛑 Stopping bot...")
    
    # Cancel all background tasks
    for task in tasks:
        task.cancel()
        try:
            await task
        except Exception:
            pass
    
    # Close all connections
    await app.exit()
    await userbot.exit()
    await db.close()
    
    logger.info("✅ Bot stopped successfully.\n")
