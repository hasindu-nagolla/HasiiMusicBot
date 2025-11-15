import time
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)
logger = logging.getLogger("HasiiMusic")


__version__ = "3.0.1"

from config import Config

config = Config()
config.check()
tasks = []
boot = time.time()

from HasiiMusic.core.bot import Bot
app = Bot()

from HasiiMusic.core.dir import ensure_dirs
ensure_dirs()

from HasiiMusic.core.userbot import Userbot
userbot = Userbot()

from HasiiMusic.core.mongo import MongoDB
db = MongoDB()

from HasiiMusic.core.lang import Language
lang = Language()

from HasiiMusic.core.telegram import Telegram
from HasiiMusic.core.youtube import YouTube
tg = Telegram()
yt = YouTube()

from HasiiMusic.helpers import Queue
queue = Queue()

from HasiiMusic.core.calls import TgCall
anon = TgCall()


async def stop() -> None:
    logger.info("Stopping...")
    for task in tasks:
        task.cancel()
        try:
            await task
        except:
            pass

    await app.exit()
    await userbot.exit()
    await db.close()

    logger.info("Stopped.\n")
