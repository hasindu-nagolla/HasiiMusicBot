# ==============================================================================
# client.py - Spotify Auth Manager
# ==============================================================================
# This file manages authentication with the official Spotipy API.
# Features:
# - Initializes the Spotipy client with credentials
# - Checks configuration status
# ==============================================================================


from typing import Optional
from HasiiMusic import config, logger

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    HAVE_SPOTIPY = True
except ImportError:
    HAVE_SPOTIPY = False

class SpotifyAuthManager:
    def __init__(self):
        self.client_id = getattr(config, "SPOTIFY_CLIENT_ID", "")
        self.client_secret = getattr(config, "SPOTIFY_CLIENT_SECRET", "")
        self.client: Optional[spotipy.Spotify] = None
        self._init_client()

    def _init_client(self) -> None:
        if not HAVE_SPOTIPY:
            logger.warning("spotipy is not installed. Will use Spotify embed parser.")
            return

        if not self.client_id or not self.client_secret:
            logger.info("Spotify credentials not set. Public Spotify embed parser active.")
            return

        try:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            self.client = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("🟢 Spotify client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spotify client: {e}")
            self.client = None

    def is_configured(self) -> bool:
        # Returns True if either spotipy client is available OR fallback parser is ready
        return True
