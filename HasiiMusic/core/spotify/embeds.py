# ==============================================================================
# embeds.py - Spotify Embed Scraper
# ==============================================================================
# This file provides a fallback HTML scraper for Spotify links.
# Features:
# - Bypasses Spotipy API rate limits using open.spotify.com/embed
# - Parses Next.js state JSON for track data
# - Caches raw tracks for paginated offsets
# ==============================================================================


import json
import re
import urllib.request
from typing import List, Tuple
from HasiiMusic import logger

class EmbedScraper:
    def __init__(self):
        # Cache for embed fallback: (item_type, item_id) -> (title, [raw_tracks])
        # Avoids re-downloading the full embed HTML on each paginated batch fetch
        self._embed_cache: dict = {}

    def fetch_embed_tracks(self, item_type: str, item_id: str, limit: int = 0, offset: int = 0) -> Tuple[str, List[dict]]:
        """Fallback extractor using Spotify embed page (bypasses 403 API restriction).

        Caches the full tracklist on first fetch so paginated batch calls
        (different offsets) slice from memory instead of re-downloading HTML.
        """
        cache_key = (item_type, item_id)

        # --- Serve from cache if available ---
        if cache_key in self._embed_cache:
            cached_title, all_tracks = self._embed_cache[cache_key]
            sliced = all_tracks[offset: offset + limit] if limit else all_tracks[offset:]
            return cached_title, sliced

        # --- Full fetch (first time only) ---
        all_raw_tracks: List[dict] = []
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
                for t in track_list:
                    title = t.get("title", "")
                    subtitle = t.get("subtitle", "")
                    duration_ms = t.get("duration", 0)
                    t_uri = t.get("uri", "")
                    t_id = t_uri.split(":")[-1] if t_uri else ""
                    t_url = f"https://open.spotify.com/track/{t_id}" if t_id else ""
                    if title:
                        all_raw_tracks.append({
                            "name": title,
                            "artists": subtitle,
                            "duration_ms": duration_ms,
                            "thumbnail": cover_thumb if item_type == "album" else "",
                            "url": t_url,
                            "id": t_id,
                        })
        except Exception as e:
            logger.debug(f"Embed parser failed for {item_type}/{item_id}: {e}")

        # Fallback to oEmbed if all_raw_tracks empty (e.g. artist or single track)
        if not all_raw_tracks or not collection_title:
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
                        if not all_raw_tracks:
                            all_raw_tracks.append({
                                "name": title,
                                "artists": "" if item_type != "artist" else "Top Tracks",
                                "duration_ms": 0,
                                "thumbnail": thumb,
                                "url": f"https://open.spotify.com/{item_type}/{item_id}",
                                "id": item_id,
                            })
            except Exception as e:
                logger.debug(f"oEmbed parser failed for {item_type}/{item_id}: {e}")

        # Store full tracklist in cache for future paginated fetches
        self._embed_cache[cache_key] = (collection_title, all_raw_tracks)
        sliced = all_raw_tracks[offset: offset + limit] if limit else all_raw_tracks[offset:]
        return collection_title, sliced
