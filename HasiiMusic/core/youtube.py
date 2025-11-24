# ==============================================================================
# youtube.py - YouTube Download & Search Handler
# ==============================================================================
# This file handles all YouTube-related operations:
# - Searching for videos/audio
# - Downloading YouTube content using yt-dlp
# - Managing YouTube cookies for age-restricted content
# - Caching search results for better performance
# - Validating YouTube URLs
# ==============================================================================

import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch
from HasiiMusic import logger
from HasiiMusic.helpers import Track, utils


class YouTube:
    def __init__(self):
        """Initialize YouTube handler with configuration and caching."""
        self.base = "https://www.youtube.com/watch?v="  # Base YouTube URL
        self.cookies = []  # List of available cookie files
        self.checked = False  # Whether cookies directory has been checked
        self.warned = False  # Whether missing cookies warning has been shown
        
        # Regular expression to match YouTube URLs (videos, shorts, playlists)
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        
        # Cache search results to reduce API calls (10 minute TTL)
        self.search_cache = {}  # {"query_video": (result, timestamp)}
        self.cache_time = {}  # Deprecated, using tuple in search_cache instead

    def get_cookies(self):
        if not self.checked:
            for file in os.listdir("HasiiMusic/cookies"):
                if file.endswith(".txt"):
                    self.cookies.append(file)
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return f"HasiiMusic/cookies/{random.choice(self.cookies)}"

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("🍪 Saving cookies from urls...")
        for url in urls:
            path = f"HasiiMusic/cookies/cookie{random.randint(10000, 99999)}.txt"
            link = url.replace("me/", "me/raw/")
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
        logger.info("✅ Cookies saved.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        messages = [message_1]
        link = None
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.URL:
                        link = text[entity.offset: entity.offset +
                                    entity.length]
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == enums.MessageEntityType.TEXT_LINK:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0].split("?si")[0]
        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        # Check cache first (10-minute TTL)
        cache_key = f"{query}_{video}"
        current_time = asyncio.get_event_loop().time()
        
        if cache_key in self.search_cache:
            cached_result, cache_timestamp = self.search_cache[cache_key]
            if current_time - cache_timestamp < 600:  # 10 minutes
                # Return cached result with new message_id
                cached_result.message_id = m_id
                return cached_result
        
        _search = VideosSearch(query, limit=1)
        results = await _search.next()
        if results and results["result"]:
            data = results["result"][0]
            duration = data.get("duration")
            is_live = duration is None or duration == "LIVE"

            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=duration if not is_live else "LIVE",
                duration_sec=0 if is_live else utils.to_seconds(duration),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get(
                    "thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
                is_live=is_live,
            )
            
            # Cache the result
            self.search_cache[cache_key] = (track, current_time)
            # Limit cache size to 100 entries
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(), key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]
            
            return track
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track]:
        plist = await Playlist.get(url)
        tracks = []
        for data in plist["videos"][:limit]:
            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name", ""),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                url=data.get("link").split("&list=")[0],
                user=user,
                view_count="",
                video=video,
            )
            tracks.append(track)
        return tracks

    async def download(self, video_id: str, video: bool = False, is_live: bool = False) -> Optional[str]:
        url = self.base + video_id

        # For live streams, extract the direct stream URL using yt-dlp with cookies
        if is_live:
            cookie = self.get_cookies()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie,
                "format": "best[height<=?720][width<=?1280]" if video else "bestaudio[acodec=opus]/bestaudio",
            }

            def _extract_url():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        return info.get("url") or info.get("manifest_url")
                    except yt_dlp.utils.ExtractorError as ex:
                        error_msg = str(ex)
                        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                            logger.error("YouTube bot detection triggered. Please update cookies.")
                        elif "not available" in error_msg.lower():
                            logger.error("Video format not available or region-blocked.")
                        else:
                            logger.error("Live stream URL extraction failed: %s", ex)
                        return None
                    except Exception as ex:
                        logger.error("Unexpected error during live stream extraction: %s", ex)
                        return None

            stream_url = await asyncio.to_thread(_extract_url)
            return stream_url if stream_url else url

        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "cookiefile": cookie,
            "continuedl": True,
            "noprogress": True,
            "concurrent_fragment_downloads": 16,
            "http_chunk_size": 1048576,  # 1MB chunks
            "socket_timeout": 15,
            "retries": 1,
            "fragment_retries": 1,
            "ignoreerrors": True,
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            # High-quality audio: Opus codec in WebM container for best quality
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]/bestaudio[acodec=opus]/bestaudio",
                "postprocessors": [],  # No post-processing to preserve original quality
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except yt_dlp.utils.ExtractorError as ex:
                    error_msg = str(ex)
                    if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                        logger.error("❌ YouTube bot detection: Please update cookies or wait before retrying.")
                    elif "not available" in error_msg.lower():
                        logger.error("❌ Video not available: May be region-blocked or private.")
                    elif "age" in error_msg.lower():
                        logger.error("❌ Age-restricted video: Cookies required.")
                    else:
                        logger.error("❌ YouTube extraction failed: %s", ex)
                    if cookie and cookie in self.cookies:
                        self.cookies.remove(cookie)
                    return None
                except yt_dlp.utils.DownloadError as ex:
                    logger.error("❌ Download error: %s", ex)
                    if cookie and cookie in self.cookies:
                        self.cookies.remove(cookie)
                    return None
                except Exception as ex:
                    logger.error("❌ Unexpected download error: %s", ex)
                    return None
            return filename

        return await asyncio.to_thread(_download)