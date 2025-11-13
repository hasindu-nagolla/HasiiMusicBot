import re
from typing import Iterable, Iterator, List, Optional, Set

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyrogram import filters


# ═══════════════════════════════════════════════════════════════════════════════
# Modern Pydantic-based Configuration
# ═══════════════════════════════════════════════════════════════════════════════


class Settings(BaseSettings):
    """
    Type-safe configuration management using Pydantic.

    All settings are loaded from environment variables with validation.
    Missing required fields will raise clear error messages.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Core Bot Config ────────────────────────────────────────────────────────
    api_id: int = Field(default=27798659, description="Telegram API ID")
    api_hash: str = Field(
        default="26100c77cee02e5e34b2bbee58440f86", description="Telegram API Hash"
    )
    bot_token: str = Field(..., description="Bot token from @BotFather")

    owner_id: int = Field(default=7044783841, description="Bot owner user ID")
    owner_username: str = Field(
        default="@Hasindu_Lakshan", description="Bot owner username"
    )
    bot_username: str = Field(default="HasiiXRobot", description="Bot username")
    bot_name: str = Field(default="˹𝐇ᴀsɪɪ ✘ 𝙼ᴜsɪᴄ˼", description="Bot display name")
    assusername: str = Field(default="musicxhasii", description="Assistant username")
    evalop: List[int] = Field(
        default_factory=lambda: [6797202080],
        description="List of user IDs with eval permissions",
    )

    # ───── Mongo & Logging ───── #
    mongo_db_uri: Optional[str] = Field(None, description="MongoDB connection URI")
    logger_id: int = Field(
        default=-1002014167331, description="Telegram chat ID for logging"
    )

    # ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────
    duration_limit: int = Field(
        default=300, description="Maximum duration for streams (minutes)"
    )
    song_download_duration: int = Field(
        default=1200, description="Maximum song download duration (seconds)"
    )
    song_download_duration_limit: int = Field(
        default=1800, description="Hard limit for song downloads (seconds)"
    )
    tg_audio_filesize_limit: int = Field(
        default=157286400, description="Telegram audio file size limit (bytes)"
    )
    tg_video_filesize_limit: int = Field(
        default=1288490189, description="Telegram video file size limit (bytes)"
    )
    playlist_fetch_limit: int = Field(
        default=30, description="Maximum number of playlist items to fetch"
    )

    # ── Streaming Quality Preferences ──────────────────────────────────────────
    stream_audio_only_quality: str = Field(
        default="studio", description="Audio-only stream quality"
    )
    stream_video_audio_quality: str = Field(
        default="studio", description="Video stream audio quality"
    )
    stream_video_quality: str = Field(
        default="fhd_1080p", description="Video stream quality"
    )
    ytdlp_audio_format: str = Field(
        default="bestaudio[abr>=256]/bestaudio/best",
        description="yt-dlp audio format selector",
    )
    ytdlp_video_format: str = Field(
        default="best[height<=?1080][width<=?1920]",
        description="yt-dlp video format selector",
    )
    ytdlp_preferred_audio_bitrate: str = Field(
        default="320", description="Preferred audio bitrate (kbps)"
    )

    # ── External APIs ──────────────────────────────────────────────────────────
    cookie_url: str = Field(..., description="URL to YouTube cookies file")
    api_url: Optional[str] = Field(None, description="Optional external API URL")
    api_key: Optional[str] = Field(None, description="Optional external API key")

    # ───── Heroku Configuration ───── #
    heroku_app_name: Optional[str] = Field(None, description="Heroku app name")
    heroku_api_key: Optional[str] = Field(None, description="Heroku API key")

    # ───── Git & Updates ───── #
    upstream_repo: str = Field(
        default="https://github.com/hasindu-nagolla/HasiiMusicBot",
        description="Upstream repository URL",
    )
    upstream_branch: str = Field(default="Master", description="Upstream branch name")
    git_token: Optional[str] = Field(None, description="GitHub personal access token")

    # ───── Support & Community ───── #
    support_channel: str = Field(
        default="https://t.me/musicxhasii", description="Support channel URL"
    )
    support_chat: str = Field(
        default="https://t.me/musicxhasii", description="Support chat URL"
    )

    # ───── Assistant Auto Leave ───── #
    auto_leaving_assistant: bool = Field(
        default=False, description="Enable auto-leave for assistant"
    )
    assistant_leave_time: int = Field(
        default=3600, description="Auto-leave timeout (seconds)"
    )

    # ───── Error Handling ───── #
    debug_ignore_log: bool = Field(default=True, description="Ignore debug logs")

    # ───── Spotify Credentials ───── #
    spotify_client_id: str = Field(
        default="22b6125bfe224587b722d6815002db2b",
        description="Spotify client ID",
    )
    spotify_client_secret: str = Field(
        default="c9c63c6fbf2f467c8bc68624851e9773",
        description="Spotify client secret",
    )

    # ───── Session Strings ───── #
    string_session: Optional[str] = Field(None, alias="STRING1", description="Primary session string")
    string_session2: Optional[str] = Field(None, description="Secondary session string")
    string_session3: Optional[str] = Field(None, description="Tertiary session string")
    string_session4: Optional[str] = Field(None, description="Quaternary session string")
    string_session5: Optional[str] = Field(None, description="Quinary session string")

    # ───── Validators ───── #
    @field_validator("evalop", mode="before")
    @classmethod
    def parse_evalop(cls, v):
        """Parse EVALOP from string or list."""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    @field_validator(
        "stream_audio_only_quality",
        "stream_video_audio_quality",
        "stream_video_quality",
        mode="after",
    )
    @classmethod
    def normalize_quality(cls, v):
        """Normalize quality settings to lowercase."""
        return v.strip().lower() if v else v

    @field_validator("ytdlp_audio_format", "ytdlp_video_format", mode="after")
    @classmethod
    def strip_format(cls, v):
        """Strip whitespace from format strings."""
        return v.strip() if v else v

    @model_validator(mode="after")
    def validate_urls(self):
        """Validate URL formats for support links and cookie URL."""
        # Validate support URLs
        if self.support_channel and not re.match(r"^https?://", self.support_channel):
            raise ValueError(
                f"Invalid SUPPORT_CHANNEL: {self.support_channel}. Must start with http:// or https://"
            )

        if self.support_chat and not re.match(r"^https?://", self.support_chat):
            raise ValueError(
                f"Invalid SUPPORT_CHAT: {self.support_chat}. Must start with http:// or https://"
            )

        # Validate cookie URL
        if not self.cookie_url:
            raise ValueError("COOKIE_URL is required")

        if not re.match(
            r"^https://(batbin\.me|pastebin\.com)/[A-Za-z0-9]+$", self.cookie_url
        ):
            raise ValueError(
                f"Invalid COOKIE_URL: {self.cookie_url}. "
                "Use https://batbin.me/<id> or https://pastebin.com/<id>"
            )

        return self

    @property
    def duration_limit_seconds(self) -> int:
        """Convert duration limit from minutes to seconds."""
        return self.duration_limit * 60


# ═══════════════════════════════════════════════════════════════════════════════
# Initialize Settings Instance
# ═══════════════════════════════════════════════════════════════════════════════

_settings = Settings()

# ═══════════════════════════════════════════════════════════════════════════════
# Backward Compatibility - Export individual variables
# ═══════════════════════════════════════════════════════════════════════════════

API_ID = _settings.api_id
API_HASH = _settings.api_hash
BOT_TOKEN = _settings.bot_token

OWNER_ID = _settings.owner_id
OWNER_USERNAME = _settings.owner_username
BOT_USERNAME = _settings.bot_username
BOT_NAME = _settings.bot_name
ASSUSERNAME = _settings.assusername
EVALOP = _settings.evalop

MONGO_DB_URI = _settings.mongo_db_uri
LOGGER_ID = _settings.logger_id

DURATION_LIMIT_MIN = _settings.duration_limit
SONG_DOWNLOAD_DURATION = _settings.song_download_duration
SONG_DOWNLOAD_DURATION_LIMIT = _settings.song_download_duration_limit
TG_AUDIO_FILESIZE_LIMIT = _settings.tg_audio_filesize_limit
TG_VIDEO_FILESIZE_LIMIT = _settings.tg_video_filesize_limit
PLAYLIST_FETCH_LIMIT = _settings.playlist_fetch_limit

STREAM_AUDIO_ONLY_QUALITY = _settings.stream_audio_only_quality
STREAM_VIDEO_AUDIO_QUALITY = _settings.stream_video_audio_quality
STREAM_VIDEO_QUALITY = _settings.stream_video_quality
YTDLP_AUDIO_FORMAT = _settings.ytdlp_audio_format
YTDLP_VIDEO_FORMAT = _settings.ytdlp_video_format
YTDLP_PREFERRED_AUDIO_BITRATE = _settings.ytdlp_preferred_audio_bitrate

COOKIE_URL = _settings.cookie_url
API_URL = _settings.api_url
API_KEY = _settings.api_key

HEROKU_APP_NAME = _settings.heroku_app_name
HEROKU_API_KEY = _settings.heroku_api_key

UPSTREAM_REPO = _settings.upstream_repo
UPSTREAM_BRANCH = _settings.upstream_branch
GIT_TOKEN = _settings.git_token

SUPPORT_CHANNEL = _settings.support_channel
SUPPORT_CHAT = _settings.support_chat

AUTO_LEAVING_ASSISTANT = _settings.auto_leaving_assistant
AUTO_LEAVE_ASSISTANT_TIME = _settings.assistant_leave_time

DEBUG_IGNORE_LOG = _settings.debug_ignore_log

SPOTIFY_CLIENT_ID = _settings.spotify_client_id
SPOTIFY_CLIENT_SECRET = _settings.spotify_client_secret

STRING1 = _settings.string_session
STRING2 = _settings.string_session2
STRING3 = _settings.string_session3
STRING4 = _settings.string_session4
STRING5 = _settings.string_session5


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

# Note: All configuration validation is now handled by pydantic in the Settings class above

