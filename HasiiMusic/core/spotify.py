# ==============================================================================
# spotify.py - Spotify Integration
# ==============================================================================
# Handles fetching Spotify playlists, albums, tracks, and artists via Spotipy API
# with intelligent embed/oembed fallback for accounts without Spotify Premium.
# Resolves metadata into streamable YouTube tracks for voice chat playback.
# ==============================================================================

import asyncio
import json
import re
import urllib.request
from typing import List, Optional, Tuple

from HasiiMusic import config, logger
from HasiiMusic.helpers import Track

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    HAVE_SPOTIPY = True
except ImportError:
    HAVE_SPOTIPY = False


class Spotify:
    def __init__(self):
        self.client_id = getattr(config, "SPOTIFY_CLIENT_ID", "")
        self.client_secret = getattr(config, "SPOTIFY_CLIENT_SECRET", "")
        self.client: Optional[spotipy.Spotify] = None
        self._init_client()

        # Match Spotify URLs & URIs (playlist, track, album, artist)
        self.url_regex = re.compile(
            r"(?:https?://)?(?:open\.)?spotify\.com/(?:intl-[a-zA-Z-]+/)?(playlist|track|album|artist)/([a-zA-Z0-9]+)(?:[?&][^\s]*)?"
        )
        self.uri_regex = re.compile(
            r"spotify:(playlist|track|album|artist):([a-zA-Z0-9]+)"
        )

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

    def _parse(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract (item_type, item_id) from Spotify URL or URI."""
        if not url:
            return None, None
        match = self.url_regex.search(url)
        if match:
            return match.group(1), match.group(2)
        match_uri = self.uri_regex.search(url)
        if match_uri:
            return match_uri.group(1), match_uri.group(2)
        return None, None

    def valid(self, url: str) -> bool:
        """Check whether the given URL is a valid Spotify link."""
        item_type, item_id = self._parse(url)
        return bool(item_type and item_id)

    def is_playlist(self, url: str) -> bool:
        """Check whether the given URL is a playlist, album, or artist collection."""
        item_type, _ = self._parse(url)
        return item_type in ("playlist", "album", "artist")

    def _fetch_embed_tracks(self, item_type: str, item_id: str, limit: int = 0) -> Tuple[str, List[str]]:
        """Fallback extractor using Spotify embed page (bypasses 403 API restriction)."""
        queries: List[str] = []
        collection_title = ""
        try:
            embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}"
            req = urllib.request.Request(
                embed_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8")

            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
            if m:
                data = json.loads(m.group(1))
                entity = data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
                collection_title = entity.get("title") or entity.get("name") or ""
                track_list = entity.get("trackList", [])
                for t in track_list:
                    title = t.get("title", "")
                    subtitle = t.get("subtitle", "")
                    if title:
                        queries.append(f"{title} {subtitle}".strip())
                    if limit and len(queries) >= limit:
                        break
        except Exception as e:
            logger.debug(f"Embed parser failed for {item_type}/{item_id}: {e}")

        # Fallback to oEmbed if queries empty (e.g. artist or single track)
        if not queries or not collection_title:
            try:
                oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/{item_type}/{item_id}"
                req = urllib.request.Request(
                    oembed_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    odata = json.loads(resp.read().decode("utf-8"))
                    title = odata.get("title")
                    if title:
                        if not collection_title:
                            collection_title = title
                        if not queries:
                            queries.append(f"{title} songs" if item_type == "artist" else title)
            except Exception as e:
                logger.debug(f"oEmbed parser failed for {item_type}/{item_id}: {e}")

        return collection_title, queries

    async def search(self, url: str, m_id: int) -> Optional[Track]:
        """Fetch a single track from Spotify and resolve to a YouTube Track."""
        from HasiiMusic import yt

        item_type, item_id = self._parse(url)
        if not item_id:
            return None

        def _fetch():
            # Try official Spotipy API first if client exists
            if self.client:
                try:
                    if item_type == "track":
                        res = self.client.track(item_id)
                        if res:
                            name = res.get("name", "")
                            artists = ", ".join(a.get("name", "") for a in res.get("artists", []))
                            return f"{name} {artists}".strip()
                except Exception:
                    pass

            # Fallback to embed / oembed
            _, tracks = self._fetch_embed_tracks(item_type, item_id, limit=1)
            return tracks[0] if tracks else None

        try:
            query = await asyncio.to_thread(_fetch)
            if not query:
                logger.warning(f"⚠️ Could not extract track details for {url}")
                return None
            logger.info(f"🎵 Spotify track resolved: '{query}'. Searching YouTube...")
            return await yt.search(query, m_id)
        except Exception as e:
            logger.error(f"❌ Spotify single track error: {e}")
            return None

    async def playlist(self, limit: int, user: str, url: str) -> List[Track]:
        """Fetch tracks from Spotify playlist/album/artist and resolve to YouTube Tracks."""
        from HasiiMusic import yt

        item_type, item_id = self._parse(url)
        if not item_id:
            return []

        def _fetch_tracks() -> Tuple[str, List[str]]:
            queries: List[str] = []
            collection_title = ""

            # 1. Try Spotipy API if configured
            if self.client:
                try:
                    if item_type == "playlist":
                        res = self.client.playlist_items(
                            item_id,
                            limit=min(limit, 100) if limit else 100,
                            additional_types=["track"],
                        )
                        items = res.get("items", []) if res else []
                        for item in items:
                            track_data = item.get("track") if isinstance(item, dict) else None
                            if not track_data or not track_data.get("name"):
                                continue
                            name = track_data.get("name", "")
                            artists = ", ".join(
                                a.get("name", "") for a in track_data.get("artists", [])
                            )
                            queries.append(f"{name} {artists}".strip())
                            if limit and len(queries) >= limit:
                                break

                    elif item_type == "album":
                        res = self.client.album_tracks(item_id, limit=min(limit, 50) if limit else 50)
                        items = res.get("items", []) if res else []
                        for item in items:
                            name = item.get("name", "")
                            artists = ", ".join(
                                a.get("name", "") for a in item.get("artists", [])
                            )
                            queries.append(f"{name} {artists}".strip())
                            if limit and len(queries) >= limit:
                                break

                    elif item_type == "artist":
                        res = self.client.artist_top_tracks(item_id)
                        tracks = res.get("tracks", []) if res else []
                        for item in tracks[:limit] if limit else tracks:
                            name = item.get("name", "")
                            artists = ", ".join(
                                a.get("name", "") for a in item.get("artists", [])
                            )
                            queries.append(f"{name} {artists}".strip())

                    if queries:
                        return collection_title, queries
                except Exception:
                    pass

            # 2. Fallback to embed/oEmbed parser (handles 403 or non-premium)
            return self._fetch_embed_tracks(item_type, item_id, limit)

        try:
            collection_title, queries = await asyncio.to_thread(_fetch_tracks)
            if not queries:
                logger.warning(f"⚠️ No tracks found in Spotify {item_type} ({item_id})")
                return []

            logger.info(f"📋 Fetched {len(queries)} tracks from Spotify {item_type} ({collection_title}). Resolving...")

            # Fast resolve first track first for instant playback
            first_track = await yt.search(queries[0], 0)
            if first_track:
                first_track.user = user
                if collection_title:
                    first_track.playlist_name = collection_title
                    first_track.playlist_url = url
                    first_track.playlist_type = item_type

            remaining_queries = queries[1:]
            results: List[Track] = [first_track] if first_track else []

            if remaining_queries:
                sem = asyncio.Semaphore(5)

                async def _resolve(q: str) -> Optional[Track]:
                    async with sem:
                        try:
                            tr = await yt.search(q, 0)
                            if tr:
                                tr.user = user
                                if collection_title:
                                    tr.playlist_name = collection_title
                                    tr.playlist_url = url
                                    tr.playlist_type = item_type
                                return tr
                        except Exception as ex:
                            logger.debug(f"YouTube resolution failed for '{q}': {ex}")
                        return None

                resolved = await asyncio.gather(*[_resolve(q) for q in remaining_queries])
                results.extend([t for t in resolved if t is not None])

            logger.info(f"✅ Resolved {len(results)}/{len(queries)} tracks from Spotify.")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to fetch Spotify playlist tracks: {e}")
            raise
