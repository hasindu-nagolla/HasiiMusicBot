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

    def _fetch_embed_tracks(self, item_type: str, item_id: str, limit: int = 0, offset: int = 0) -> Tuple[str, List[dict]]:
        """Fallback extractor using Spotify embed page (bypasses 403 API restriction)."""
        raw_tracks: List[dict] = []
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
                cover_art = entity.get("coverArt", {})
                cover_sources = cover_art.get("sources", []) if isinstance(cover_art, dict) else []
                cover_thumb = cover_sources[0].get("url", "") if cover_sources else ""
                track_list = entity.get("trackList", [])
                for idx, t in enumerate(track_list):
                    if idx < offset:
                        continue
                    title = t.get("title", "")
                    subtitle = t.get("subtitle", "")
                    duration_ms = t.get("duration", 0)
                    t_uri = t.get("uri", "")
                    t_id = t_uri.split(":")[-1] if t_uri else ""
                    t_url = f"https://open.spotify.com/track/{t_id}" if t_id else ""
                    if title:
                        raw_tracks.append({
                            "name": title,
                            "artists": subtitle,
                            "duration_ms": duration_ms,
                            "thumbnail": cover_thumb,
                            "url": t_url,
                            "id": t_id,
                        })
                    if limit and len(raw_tracks) >= limit:
                        break
        except Exception as e:
            logger.debug(f"Embed parser failed for {item_type}/{item_id}: {e}")

        # Fallback to oEmbed if raw_tracks empty (e.g. artist or single track)
        if not raw_tracks or not collection_title:
            try:
                oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/{item_type}/{item_id}"
                req = urllib.request.Request(
                    oembed_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    odata = json.loads(resp.read().decode("utf-8"))
                    title = odata.get("title")
                    thumb = odata.get("thumbnail_url", "")
                    if title:
                        if not collection_title:
                            collection_title = title
                        if not raw_tracks and offset == 0:
                            raw_tracks.append({
                                "name": title,
                                "artists": "" if item_type != "artist" else "Top Tracks",
                                "duration_ms": 0,
                                "thumbnail": thumb,
                                "url": f"https://open.spotify.com/{item_type}/{item_id}",
                                "id": item_id,
                            })
            except Exception as e:
                logger.debug(f"oEmbed parser failed for {item_type}/{item_id}: {e}")

        return collection_title, raw_tracks

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
            if tracks:
                t = tracks[0]
                name = t.get("name", "")
                artists = t.get("artists", "")
                return f"{name} {artists}".strip() if artists else name
            return None

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

    async def playlist(self, limit: int, user: str, url: str, offset: int = 0) -> List[Track]:
        """Fetch raw track metadata from Spotify playlist/album/artist without resolving YouTube links."""
        from HasiiMusic.helpers import utils

        item_type, item_id = self._parse(url)
        if not item_id:
            return []

        def _fetch_tracks() -> Tuple[str, List[dict]]:
            raw_tracks: List[dict] = []
            collection_title = ""

            # 1. Try Spotipy API if configured
            if self.client:
                try:
                    if item_type == "playlist":
                        pl_info = self.client.playlist(item_id, fields="name,images")
                        collection_title = pl_info.get("name", "") if pl_info else ""
                        pl_images = pl_info.get("images", []) if pl_info else []
                        cover_thumb = pl_images[0].get("url", "") if pl_images else ""

                        res = self.client.playlist_items(
                            item_id,
                            limit=min(limit, 100) if limit else 100,
                            offset=offset,
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
                            duration_ms = track_data.get("duration_ms", 0)
                            images = track_data.get("album", {}).get("images", [])
                            thumb = images[0].get("url", "") if images else cover_thumb
                            t_id = track_data.get("id", "")
                            t_url = track_data.get("external_urls", {}).get("spotify") or (
                                f"https://open.spotify.com/track/{t_id}" if t_id else url
                            )
                            raw_tracks.append({
                                "name": name,
                                "artists": artists,
                                "duration_ms": duration_ms,
                                "thumbnail": thumb,
                                "url": t_url,
                                "id": t_id,
                            })
                            if limit and len(raw_tracks) >= limit:
                                break

                    elif item_type == "album":
                        album_info = self.client.album(item_id)
                        collection_title = album_info.get("name", "") if album_info else ""
                        album_images = album_info.get("images", []) if album_info else []
                        album_thumb = album_images[0].get("url", "") if album_images else ""

                        res = self.client.album_tracks(
                            item_id,
                            limit=min(limit, 50) if limit else 50,
                            offset=offset,
                        )
                        items = res.get("items", []) if res else []
                        for item in items:
                            name = item.get("name", "")
                            artists = ", ".join(
                                a.get("name", "") for a in item.get("artists", [])
                            )
                            duration_ms = item.get("duration_ms", 0)
                            t_id = item.get("id", "")
                            t_url = item.get("external_urls", {}).get("spotify") or (
                                f"https://open.spotify.com/track/{t_id}" if t_id else url
                            )
                            raw_tracks.append({
                                "name": name,
                                "artists": artists,
                                "duration_ms": duration_ms,
                                "thumbnail": album_thumb,
                                "url": t_url,
                                "id": t_id,
                            })
                            if limit and len(raw_tracks) >= limit:
                                break

                    elif item_type == "artist":
                        artist_info = self.client.artist(item_id)
                        collection_title = artist_info.get("name", "") if artist_info else ""
                        artist_images = artist_info.get("images", []) if artist_info else []
                        artist_thumb = artist_images[0].get("url", "") if artist_images else ""

                        res = self.client.artist_top_tracks(item_id)
                        tracks = res.get("tracks", []) if res else []
                        selected_tracks = tracks[offset:offset+limit] if limit else tracks[offset:]
                        for item in selected_tracks:
                            name = item.get("name", "")
                            artists = ", ".join(
                                a.get("name", "") for a in item.get("artists", [])
                            )
                            duration_ms = item.get("duration_ms", 0)
                            images = item.get("album", {}).get("images", [])
                            thumb = images[0].get("url", "") if images else artist_thumb
                            t_id = item.get("id", "")
                            t_url = item.get("external_urls", {}).get("spotify") or (
                                f"https://open.spotify.com/track/{t_id}" if t_id else url
                            )
                            raw_tracks.append({
                                "name": name,
                                "artists": artists,
                                "duration_ms": duration_ms,
                                "thumbnail": thumb,
                                "url": t_url,
                                "id": t_id,
                            })

                    if raw_tracks:
                        return collection_title, raw_tracks
                except Exception as ex:
                    logger.debug(f"Spotipy client fetch failed for {item_type}/{item_id}: {ex}")

            # 2. Fallback to embed/oEmbed parser
            return self._fetch_embed_tracks(item_type, item_id, limit, offset=offset)

        try:
            collection_title, raw_tracks = await asyncio.to_thread(_fetch_tracks)
            if not raw_tracks:
                logger.warning(f"⚠️ No tracks found in Spotify {item_type} ({item_id}) at offset {offset}")
                return []

            tracks: List[Track] = []
            for i, raw in enumerate(raw_tracks, start=offset + 1):
                name = raw.get("name", "")
                artists = raw.get("artists", "")
                query = f"{name} {artists}".strip() if artists else name
                duration_sec = int(raw.get("duration_ms", 0) // 1000)
                duration = utils.format_duration(duration_sec) if duration_sec else "0:00"

                track = Track(
                    id=query,
                    channel_name=artists,
                    duration=duration,
                    duration_sec=duration_sec,
                    title=name[:25],
                    thumbnail=raw.get("thumbnail", ""),
                    url=raw.get("url") or url,
                    user=user,
                    view_count="",
                    playlist_name=collection_title or f"Spotify {item_type.capitalize()}",
                    playlist_url=url,
                    playlist_type=item_type,
                    playlist_index=i,
                )
                tracks.append(track)

            logger.info(f"📋 Loaded {len(tracks)} raw tracks (offset {offset}) from Spotify {item_type} ({collection_title}).")
            return tracks

        except Exception as e:
            logger.error(f"❌ Failed to fetch Spotify playlist tracks: {e}")
            raise
