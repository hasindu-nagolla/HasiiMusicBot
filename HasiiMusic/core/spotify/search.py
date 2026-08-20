# ==============================================================================
# search.py - Spotify Search Manager
# ==============================================================================
# This file resolves Spotify metadata and links it to YouTube.
# Features:
# - Uses Spotipy client or fallback embed scraper dynamically
# - Formats raw data into uniform Track objects
# - Lazily queries YouTube to find playable audio links
# ==============================================================================


import asyncio
from typing import List, Optional, Tuple
from HasiiMusic import logger
from HasiiMusic.helpers import Track

class SpotifySearcher:
    def __init__(self, auth_manager, embed_scraper, utils):
        self._auth = auth_manager
        self._embeds = embed_scraper
        self._utils = utils

    async def search(self, url: str, m_id: int) -> Optional[Track]:
        """Fetch a single track from Spotify and resolve to a YouTube Track."""
        # Lazy import to avoid circular dependencies (HasiiMusic.yt imports Spotify)
        from HasiiMusic import yt

        item_type, item_id = self._utils._parse(url)
        if not item_id:
            return None

        def _fetch():
            # Try official Spotipy API first if client exists
            if self._auth.client:
                try:
                    if item_type == "track":
                        res = self._auth.client.track(item_id)
                        if res:
                            name = res.get("name", "")
                            artists = ", ".join(a.get("name", "") for a in res.get("artists", []))
                            return f"{name} {artists}".strip()
                except Exception:
                    pass

            # Fallback to embed / oembed
            _, tracks = self._embeds.fetch_embed_tracks(item_type, item_id, limit=1)
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
            return await yt.search(query, m_id, music=True)
        except Exception as e:
            logger.error(f"❌ Spotify single track error: {e}")
            return None

    async def playlist(self, limit: int, user: str, url: str, offset: int = 0) -> List[Track]:
        """Fetch raw track metadata from Spotify playlist/album/artist without resolving YouTube links."""
        from HasiiMusic.helpers import utils

        item_type, item_id = self._utils._parse(url)
        if not item_id:
            return []

        def _fetch_tracks() -> Tuple[str, List[dict]]:
            raw_tracks: List[dict] = []
            collection_title = ""

            # 1. Try Spotipy API if configured
            if self._auth.client:
                try:
                    if item_type == "playlist":
                        pl_info = self._auth.client.playlist(item_id, fields="name,images")
                        collection_title = pl_info.get("name", "") if pl_info else ""
                        pl_images = pl_info.get("images", []) if pl_info else []
                        cover_thumb = pl_images[0].get("url", "") if pl_images else ""

                        res = self._auth.client.playlist_items(
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
                            thumb = images[0].get("url", "") if images else (cover_thumb if item_type == "album" else "")
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
                        album_info = self._auth.client.album(item_id)
                        collection_title = album_info.get("name", "") if album_info else ""
                        album_images = album_info.get("images", []) if album_info else []
                        album_thumb = album_images[0].get("url", "") if album_images else ""

                        res = self._auth.client.album_tracks(
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
                        artist_info = self._auth.client.artist(item_id)
                        collection_title = artist_info.get("name", "") if artist_info else ""
                        artist_images = artist_info.get("images", []) if artist_info else []
                        artist_thumb = artist_images[0].get("url", "") if artist_images else ""

                        res = self._auth.client.artist_top_tracks(item_id)
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
            return self._embeds.fetch_embed_tracks(item_type, item_id, limit, offset=offset)

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


            return tracks

        except Exception as e:
            logger.error(f"❌ Failed to fetch Spotify playlist tracks: {e}")
            raise
