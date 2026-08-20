# ==============================================================================
# __init__.py - Spotify Facade
# ==============================================================================
# This file serves as the main entry point for Spotify integration.
# Features:
# - Exposes the public API for the Spotify class
# - Initializes and delegates to modular sub-components
# ==============================================================================


from typing import List, Optional
from HasiiMusic.helpers import Track

from .utils import SpotifyUtils
from .client import SpotifyAuthManager
from .embeds import EmbedScraper
from .search import SpotifySearcher

class Spotify:
    def __init__(self):
        self._utils = SpotifyUtils()
        self._auth = SpotifyAuthManager()
        self._embeds = EmbedScraper()
        
        # Dependency Injection
        self._searcher = SpotifySearcher(self._auth, self._embeds, self._utils)

    # --- Utils ---
    def valid(self, url: str) -> bool:
        """Check whether the given URL is a valid Spotify link."""
        return self._utils.valid(url)

    def is_playlist(self, url: str) -> bool:
        """Check whether the given URL is a playlist, album, or artist collection."""
        return self._utils.is_playlist(url)

    # --- Search & Playlist ---
    async def search(self, url: str, m_id: int) -> Optional[Track]:
        """Fetch a single track from Spotify and resolve to a YouTube Track."""
        return await self._searcher.search(url, m_id)

    async def playlist(self, limit: int, user: str, url: str, offset: int = 0) -> List[Track]:
        """Fetch raw track metadata from Spotify playlist/album/artist without resolving YouTube links."""
        return await self._searcher.playlist(limit, user, url, offset)

    # --- Config ---
    def is_configured(self) -> bool:
        """Returns True if either spotipy client is available OR fallback parser is ready."""
        return self._auth.is_configured()
