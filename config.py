import re
import os
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file
load_dotenv()

# ───── Basic Bot Configuration ───── #
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID", 7044783841))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "CertifiedCoder")
BOT_USERNAME = os.getenv("BOT_USERNAME", "HasiiXRobot")
BOT_NAME = os.getenv("BOT_NAME", "˹𝐇ᴀsɪɪ ✘ 𝙼ᴜsɪᴄ˼ ♪")
ASSUSERNAME = os.getenv("ASSUSERNAME", "musicxhasii")
EVALOP = list(map(int, os.getenv("EVALOP", "6797202080").split()))

# ───── Mongo & Logging ───── #
MONGO_DB_URI = os.getenv("MONGO_DB_URI")
LOGGER_ID = int(os.getenv("LOGGER_ID", -1002014167331))

# ───── Limits and Durations ───── #
RESTART_INTERVAL = int(
    os.getenv("RESTART_INTERVAL", 86400))  # default 24 hours
DURATION_LIMIT_MIN = int(os.getenv("DURATION_LIMIT", 17000))
SONG_DOWNLOAD_DURATION = int(os.getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(
    os.getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
TG_AUDIO_FILESIZE_LIMIT = int(
    os.getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(
    os.getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

# ───── Custom API Configs ───── #
API_URL = os.getenv("API_URL")  # optional
API_KEY = os.getenv("API_KEY")  # optional
COOKIE_URL = os.getenv("COOKIE_URL")  # necessary
DEEP_API = os.getenv("DEEP_API")  # optional

# ───── Heroku Configuration ───── #
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY")

# ───── Git & Updates ───── #
UPSTREAM_REPO = os.getenv(
    "UPSTREAM_REPO", "https://github.com/CertifiedCoders/AnnieXMusic")
UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = os.getenv("GIT_TOKEN")

# ───── Support & Community ───── #
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/CertifiedNetwork")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/CertifiedDiscussion")

# ───── Assistant Auto Leave ───── #
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = int(os.getenv("ASSISTANT_LEAVE_TIME", "11500"))

# ───── Error Handling ───── #
DEBUG_IGNORE_LOG = True

# ───── Spotify Credentials ───── #
SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = os.getenv(
    "SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ───── Session Strings ───── #
STRING1 = os.getenv("STRING_SESSION")
STRING2 = os.getenv("STRING_SESSION2")
STRING3 = os.getenv("STRING_SESSION3")
STRING4 = os.getenv("STRING_SESSION4")
STRING5 = os.getenv("STRING_SESSION5")

# ───── Server Settings ───── #
SERVER_PLAYLIST_LIMIT = int(os.getenv("SERVER_PLAYLIST_LIMIT", "3000"))
PLAYLIST_FETCH_LIMIT = int(os.getenv("PLAYLIST_FETCH_LIMIT", "2500"))

# ───── Bot Media Assets ───── #
START_VIDS = [
    "https://telegra.ph/file/9b7e1b820c72a14d90be7.mp4",
    "https://telegra.ph/file/72f349b1386d6d9374a38.mp4",
    "https://telegra.ph/file/a4d90b0cb759b67d68644.mp4"
]

STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ"
]
HELP_IMG_URL = "https://files.catbox.moe/139oue.png"
PING_VID_URL = "https://files.catbox.moe/hssx04.png"
PLAYLIST_IMG_URL = "https://files.catbox.moe/k2yqsd.png"
STATS_VID_URL = "https://telegra.ph/file/e2ab6106ace2e95862372.mp4"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/bnzdl9.png"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/bnzdl9.png"
STREAM_IMG_URL = "https://files.catbox.moe/bnzdl9.png"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/bnzdl9.png"
YOUTUBE_IMG_URL = "https://files.catbox.moe/bnzdl9.png"
SPOTIFY_ARTIST_IMG_URL = SPOTIFY_ALBUM_IMG_URL = SPOTIFY_PLAYLIST_IMG_URL = YOUTUBE_IMG_URL

# ───── Bot Access Restriction (Group/User Whitelist) ───── #
allowed_str = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = [int(i) for i in allowed_str.split(",") if i]

# ───── Utility & Functional ───── #


def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))


DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Bot Introduction Messages ───── #
# AYU = ["💞", "🦋", "🔍"]
# AYU = ["Processing", "Searching", "Loading", "Connecting", "Preparing", "Almost Done", "Verifying", "Starting", "Getting Ready", "Just a Moment", "Hopping", "Warming Up", "Booting Up", "Optimizing"]
# AYU = ["Processing...", "Searching...", "Loading...", "Connecting...", "Preparing...", "Almost Done...", "Verifying...", "Starting...", "Getting Ready...", "Just a Moment...", "Hopping...", "Warming Up...", "Booting Up...", "Optimizing..."]
AYU = [
     "▰▱▱▱▱▱▱▱▱ Processing... 💞",
    "▰▰▱▱▱▱▱▱▱ Searching... 🔍",
    "▰▰▰▱▱▱▱▱▱ Loading... ⚡",
    "▰▰▰▰▱▱▱▱▱ Connecting... 🌐",
    "▰▰▰▰▰▱▱▱▱ Preparing... 🔧",
    "▰▰▰▰▰▰▱▱▱ Almost Done... ⏳",
    "▰▰▰▰▰▰▰▱▱ Verifying... 🛡️",
    "▰▰▰▰▰▰▰▰▱ Starting... 🦋",
    "▰▰▰▰▰▰▰▰▰ Ready 🚀",
    "💞", "🦋", "🔍", "🧪", "⚡️", "🔥", "🎩", "🌈", "🍷", "🥂", "🥃", "🕊️", "🪄", "💌", "🧨"
]
AYUV = [
    "ʜᴇʟʟᴏ {0}, 🥀\n\n ɪᴛ'ꜱ ᴍᴇ {1} !\n\n┏━━━━━━━━━━━━━━━━━⧫\n┠ ◆ ꜱᴜᴘᴘᴏʀᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍꜱ : ʏᴏᴜᴛᴜʙᴇ, ꜱᴘᴏᴛɪꜰʏ,\n┠ ◆ ʀᴇꜱꜱᴏ, ᴀᴘᴘʟᴇᴍᴜꜱɪᴄ , ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ ᴇᴛᴄ.\n┗━━━━━━━━━━━━━━━━━⧫\n┏━━━━━━━━━━━━━━━━━⧫\n┠ ➥ Uᴘᴛɪᴍᴇ : {2}\n┠ ➥ SᴇʀᴠᴇʀSᴛᴏʀᴀɢᴇ : {3}\n┠ ➥ CPU Lᴏᴀᴅ : {4}\n┠ ➥ RAM Cᴏɴsᴜᴘᴛɪᴏɴ : {5}\n┠ ➥ ᴜꜱᴇʀꜱ : {6}\n┠ ➥ ᴄʜᴀᴛꜱ : {7}\n┗━━━━━━━━━━━━━━━━━⧫\n\n🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🪽 ➪ [ᴄᴇʀᴛɪғɪᴇᴅ ᴄᴏᴅᴇʀ ✔︎](https://t.me/CertifiedCoder)",
    "ʜɪɪ, {0} ~\n\n◆ ɪ'ᴍ ᴀ {1} ᴛᴇʟᴇɢʀᴀᴍ ꜱᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ ᴡɪᴛʜ ꜱᴏᴍᴇ ᴜꜱᴇꜰᴜʟ\n◆ ᴜʟᴛʀᴀ ғᴀsᴛ ᴠᴄ ᴘʟᴀʏᴇʀ ꜰᴇᴀᴛᴜʀᴇꜱ.\n\n✨ ꜰᴇᴀᴛᴜʀᴇꜱ ⚡️\n◆ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs.\n◆ Sᴜᴘᴇʀғᴀsᴛ ʟᴀɢ Fʀᴇᴇ ᴘʟᴀʏᴇʀ.\n◆ ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴍᴜꜱɪᴄ + ᴠɪᴅᴇᴏ.\n◆ ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍɪɴɢ.\n◆ ɴᴏ ᴘʀᴏᴍᴏ.\n◆ ʙᴇꜱᴛ ꜱᴏᴜɴᴅ Qᴜᴀʟɪᴛʏ.\n◆ 24×7 ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴍᴜꜱɪᴄ.\n◆ ᴀᴅᴅ ᴛʜɪꜱ ʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ɪᴛ ᴀᴅᴍɪɴ ᴀɴᴅ ᴇɴᴊᴏʏ ᴍᴜꜱɪᴄ 🎵.\n\n┏━━━━━━━━━━━━━━━━━⧫\n┠ ◆ ꜱᴜᴘᴘᴏʀᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍꜱ : ʏᴏᴜᴛᴜʙᴇ, ꜱᴘᴏᴛɪꜰʏ,\n┠ ◆ ʀᴇꜱꜱᴏ, ᴀᴘᴘʟᴇᴍᴜꜱɪᴄ , ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ ᴇᴛᴄ.\n┗━━━━━━━━━━━━━━━━━⧫\n┏━━━━━━━━━━━━━━━━━⧫\n┠ ➥ Uᴘᴛɪᴍᴇ : {2}\n┠ ➥ SᴇʀᴠᴇʀSᴛᴏʀᴀɢᴇ : {3}\n┠ ➥ CPU Lᴏᴀᴅ : {4}\n┠ ➥ RAM Cᴏɴsᴜᴘᴛɪᴏɴ : {5}\n┠ ➥ ᴜꜱᴇʀꜱ : {6}\n┠ ➥ ᴄʜᴀᴛꜱ : {7}\n┗━━━━━━━━━━━━━━━━━⧫\n\n🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🪽 ➪ [ᴄᴇʀᴛɪғɪᴇᴅ ᴄᴏᴅᴇʀ ✔︎](https://t.me/CertifiedCoder)",
]

# ───── Runtime Structures ───── #
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ───── URL Validation ───── #
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit(
        "[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit(
        "[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")
