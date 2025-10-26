import re
from os import getenv
from dotenv import load_dotenv
from typing import Iterable, Iterator, Set

from pyrogram import filters

# Load environment variables from .env file
load_dotenv()

# ── Core bot config ────────────────────────────────────────────────────────────
API_ID = int(getenv("API_ID", 27798659))
API_HASH = getenv("API_HASH", "26100c77cee02e5e34b2bbee58440f86")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_ID = int(getenv("OWNER_ID", 7044783841))
OWNER_USERNAME = getenv("OWNER_USERNAME", "@Hasindu_Lakshan")
BOT_USERNAME = getenv("BOT_USERNAME", "HasiiXRobot")
BOT_NAME = getenv("BOT_NAME", "˹𝐇ᴀsɪɪ ✘ 𝙼ᴜsɪᴄ˼")
ASSUSERNAME = getenv("ASSUSERNAME", "musicxhasii")
EVALOP = list(map(int, getenv("EVALOP", "6797202080").split()))

# ───── Mongo & Logging ───── #
MONGO_DB_URI = getenv("MONGO_DB_URI")
LOGGER_ID = int(getenv("LOGGER_ID", -1002014167331))

# ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "1200"))
SONG_DOWNLOAD_DURATION_LIMIT = int(
    getenv("SONG_DOWNLOAD_DURATION_LIMIT", "1800"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "157286400"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1288490189"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "30"))

# ── Streaming quality preferences ────────────────────────────────────────────
STREAM_AUDIO_ONLY_QUALITY = getenv(
    "STREAM_AUDIO_ONLY_QUALITY", "studio"
).strip().lower()
STREAM_VIDEO_AUDIO_QUALITY = getenv(
    "STREAM_VIDEO_AUDIO_QUALITY", "studio"
).strip().lower()
STREAM_VIDEO_QUALITY = getenv(
    "STREAM_VIDEO_QUALITY", "fhd_1080p"
).strip().lower()
YTDLP_AUDIO_FORMAT = getenv(
    "YTDLP_AUDIO_FORMAT", "bestaudio[abr>=256]/bestaudio/best"
).strip()
YTDLP_VIDEO_FORMAT = getenv(
    "YTDLP_VIDEO_FORMAT", "best[height<=?1080][width<=?1920]"
).strip()
YTDLP_PREFERRED_AUDIO_BITRATE = getenv(
    "YTDLP_PREFERRED_AUDIO_BITRATE", "320"
).strip()

# ── External APIs ──────────────────────────────────────────────────────────────
COOKIE_URL = getenv("COOKIE_URL")  # required (paste link)
API_URL = getenv("API_URL")        # optional
API_KEY = getenv("API_KEY")        # optional

# ───── Heroku Configuration ───── #
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# ───── Git & Updates ───── #
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO", "https://github.com/hasindu-nagolla/HasiiMusicBot")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = getenv("GIT_TOKEN")

# ───── Support & Community ───── #
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/musicxhasii")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/musicxhasii")

# ───── Assistant Auto Leave ───── #
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "3600"))

# ───── Error Handling ───── #
DEBUG_IGNORE_LOG = True

# ───── Spotify Credentials ───── #
SPOTIFY_CLIENT_ID = getenv(
    "SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv(
    "SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ───── Session Strings ───── #
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")


# ───── Bot Media Assets ───── #
START_VIDS = [
    "https://files.catbox.moe/c3nt3q.mp4",
    "https://files.catbox.moe/0g8sfl.mp4",
    "https://files.catbox.moe/v0izu5.mp4"
]

STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ"
]
HELP_IMG_URL = "https://files.catbox.moe/139oue.png"
PING_VID_URL = "https://files.catbox.moe/xn7qae.png"
PLAYLIST_IMG_URL = "https://files.catbox.moe/isq0xv.png"
STATS_VID_URL = "https://files.catbox.moe/fcdh4j.png"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/wal0ys.png"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/q06uki.png"
STREAM_IMG_URL = "https://files.catbox.moe/q8j61o.png"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/000ozd.png"
YOUTUBE_IMG_URL = "https://files.catbox.moe/rt7nxl.png"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/5zitrm.png"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/5zitrm.png"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/5zitrm.png"
FAILED = "https://files.catbox.moe/rt7nxl.png"


# ───── Utility & Functional ───── #
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))


DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")


# ───── Bot Introduction Messages ───── #
AYU = ["💞", "🦋", "🔍", "🧪", "⚡️", "🎩", "🍷", "🥂", "🕊️", "🪄", "🧨"]

# ───── Runtime Structures ───── #
class BannedUsersManager:
    """Manage banned user IDs while exposing a Pyrogram filter."""

    def __init__(self) -> None:
        self._ids: Set[int] = set()

        def _checker(_, __, update) -> bool:
            user = getattr(update, "from_user", None)
            return bool(user and user.id in self._ids)

        self._filter = filters.create(_checker)

    def add(self, user_id: int) -> None:
        self._ids.add(int(user_id))

    def remove(self, user_id: int) -> None:
        self._ids.remove(int(user_id))

    def discard(self, user_id: int) -> None:
        self._ids.discard(int(user_id))

    def update(self, user_ids: Iterable[int]) -> None:
        for user_id in user_ids:
            self.add(user_id)

    def clear(self) -> None:
        self._ids.clear()

    def __contains__(self, user_id: object) -> bool:  # type: ignore[override]
        try:
            return int(user_id) in self._ids
        except (TypeError, ValueError):
            return False

    def __len__(self) -> int:
        return len(self._ids)

    def __iter__(self) -> Iterator[int]:
        return iter(self._ids)

    def __bool__(self) -> bool:
        return bool(self._ids)

    def __invert__(self):
        return ~self._filter

    def __repr__(self) -> str:
        return f"BannedUsersManager(total={len(self)})"

    @property
    def filter(self):
        return self._filter


BANNED_USERS = BannedUsersManager()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ── Minimal validation ─────────────────────────────────────────────────────────
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit(
        "[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit(
        "[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")

if not COOKIE_URL:
    raise SystemExit("[ERROR] - COOKIE_URL is required.")

# Only allow these cookie link formats
if not re.match(r"^https://(batbin\.me|pastebin\.com)/[A-Za-z0-9]+$", COOKIE_URL):
    raise SystemExit(
        "[ERROR] - Invalid COOKIE_URL. Use https://batbin.me/<id> or https://pastebin.com/<id>")

