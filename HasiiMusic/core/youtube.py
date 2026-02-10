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

        # **PERFORMANCE FIX**: Limit concurrent downloads to prevent bandwidth saturation
        # With 15-20 groups, unlimited concurrent downloads cause 320+ connections
        self._download_semaphore = asyncio.Semaphore(5)  # Max 5 simultaneous downloads

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
        saved_count = 0
        for url in urls:
            try:
                path = f"HasiiMusic/cookies/cookie{random.randint(10000, 99999)}.txt"
                link = url.replace("me/", "me/raw/")
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as resp:
                        if resp.status != 200:
                            logger.error(f"❌ Cookie download failed: HTTP {resp.status} from {url}")
                            continue
                        content = await resp.read()
                        if not content or len(content) < 50:
                            logger.error(f"❌ Cookie file empty or invalid from {url}")
                            continue
                        with open(path, "wb") as fw:
                            fw.write(content)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            saved_count += 1
                            # Add the new cookie file to the list immediately
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"✅ Saved: {cookie_filename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Cookie download error from {url}: {e}")
        
        # Force refresh of cookie list after download
        self.checked = True
        
        if saved_count > 0:
            logger.info(f"✅ Cookies saved. ({saved_count} file(s))")
        else:
            logger.error("❌ No cookies saved! Check COOKIE_URL in .env. YouTube downloads will fail!")

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

    async def search(self, query: str, m_id: int) -> Track | None:
        # Check cache first (10-minute TTL)
        cache_key = query
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
                is_live=is_live,
            )

            # Cache the result
            self.search_cache[cache_key] = (track, current_time)
            # Limit cache size to 100 entries
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(),
                                 key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]

            return track
        return None

    async def playlist(self, limit: int, user: str, url: str) -> list[Track]:
        try:
            plist = await Playlist.get(url)
            tracks = []

            # Check if plist has videos
            if not plist or "videos" not in plist or not plist["videos"]:
                return []

            for data in plist["videos"][:limit]:
                try:
                    # Get thumbnail safely
                    thumbnails = data.get("thumbnails", [])
                    thumbnail_url = ""
                    if thumbnails and len(thumbnails) > 0:
                        thumbnail_url = thumbnails[-1].get(
                            "url", "").split("?")[0]

                    # Get link safely
                    link = data.get("link", "")
                    if "&list=" in link:
                        link = link.split("&list=")[0]

                    track = Track(
                        id=data.get("id", ""),
                        channel_name=data.get("channel", {}).get("name", ""),
                        duration=data.get("duration", "0:00"),
                        duration_sec=utils.to_seconds(
                            data.get("duration", "0:00")),
                        title=(data.get("title", "Unknown")[:25]),
                        thumbnail=thumbnail_url,
                        url=link,
                        user=user,
                        view_count="",
                    )
                    tracks.append(track)
                except Exception as e:
                    # Skip individual track errors
                    continue

            return tracks
        except KeyError as e:
            # Handle YouTube API structure changes
            raise Exception(
                f"Failed to parse playlist. YouTube may have changed their structure.")
        except Exception as e:
            # Re-raise other exceptions
            raise

    async def download(self, video_id: str, is_live: bool = False) -> Optional[str]:
        url = self.base + video_id

        # For live streams, extract the direct stream URL using yt-dlp with cookies
        if is_live:
            cookie = self.get_cookies()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie,
                "format": "bestaudio/best",
            }

            def _extract_url():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        return info.get("url") or info.get("manifest_url")
                    except yt_dlp.utils.ExtractorError as ex:
                        error_msg = str(ex)
                        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                            logger.error(
                                "YouTube bot detection triggered. Please update cookies.")
                        elif "not available" in error_msg.lower():
                            logger.error(
                                "Video format not available or region-blocked.")
                        else:
                            logger.error(
                                "Live stream URL extraction failed: %s", ex)
                        return None
                    except yt_dlp.utils.DownloadError as ex:
                        error_msg = str(ex)
                        if "failed to load cookies" in error_msg.lower() or "netscape format" in error_msg.lower():
                            logger.error(
                                "❌ Corrupted cookie file detected for live stream, removing: %s", cookie)
                            # Remove corrupted cookie
                            if cookie and cookie in self.cookies:
                                self.cookies.remove(cookie)
                            try:
                                os.remove(f"HasiiMusic/cookies/{cookie}")
                            except:
                                pass
                        else:
                            logger.error(
                                "Unexpected error during live stream extraction: %s", ex)
                        return None
                    except Exception as ex:
                        logger.error(
                            "Unexpected error during live stream extraction: %s", ex)
                        return None

            stream_url = await asyncio.to_thread(_extract_url)
            return stream_url if stream_url else url

        # Download audio file
        # Don't hardcode extension - let yt-dlp choose best available audio format
        # Will use outtmpl pattern to get actual extension
        filename_pattern = f"downloads/{video_id}"
        
        # Check if any audio file with this video_id already exists
        import glob
        existing_files = glob.glob(f"{filename_pattern}.*")
        if existing_files:
            # Filter out .part files
            existing_files = [f for f in existing_files if not f.endswith('.part')]
            if existing_files:
                return existing_files[0]  # Return first match
        
        # Ensure downloads directory exists with write permissions
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            try:
                downloads_dir.mkdir(parents=True, exist_ok=True)
                logger.info("📁 Created downloads directory")
            except Exception as e:
                logger.error(f"❌ Cannot create downloads directory: {e}")
                return None

        # **PERFORMANCE FIX**: Use semaphore to limit concurrent downloads
        # Prevents bandwidth saturation when 15-20 groups download simultaneously
        async with self._download_semaphore:
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
                # **PERFORMANCE FIX**: Reduced to 4 fragments for maximum stability
                # 4 fragments × 5 concurrent downloads = 20 total connections (prevents bandwidth saturation)
                # Lower = more stable but slightly slower downloads (trade-off for zero lag)
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 524288,  # 512KB chunks (smaller = more stable streaming)
                "socket_timeout": 30,  # Increased from 15s (prevents timeout on slow networks)
                "retries": 2,  # Increased from 1 (better reliability)
                "fragment_retries": 2,  # Increased from 1 (handle network hiccups)
                "ignoreerrors": True,
            }

            # Audio-only: Prefer Opus codec (best quality) but accept any audio format
            # Don't force WebM container - let YouTube provide whatever's available
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[acodec=opus]/bestaudio/best",
                "postprocessors": [],  # No post-processing to preserve original quality
            }

            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        # Extract info to get actual extension downloaded
                        info = ydl.extract_info(url, download=True)
                        if not info:
                            logger.error(f"❌ Failed to extract info for {video_id}")
                            return None
                        
                        # Get actual extension from downloaded file
                        actual_ext = info.get('ext', 'webm')
                        actual_filename = f"downloads/{video_id}.{actual_ext}"
                        
                        # Check if file exists
                        if Path(actual_filename).exists():
                            logger.info(f"✅ Downloaded: {actual_filename} ({actual_ext} format)")
                            return actual_filename
                        
                        # Wait for filesystem operations to complete
                        import time
                        import glob
                        time.sleep(2.0)
                        
                        if Path(actual_filename).exists():
                            return actual_filename
                        
                        # Try to find .part file and rename it
                        part_file = Path(f"{actual_filename}.part")
                        if part_file.exists():
                            try:
                                import shutil
                                shutil.move(str(part_file), actual_filename)
                                logger.info(f"✅ Renamed .part file to {actual_filename}")
                                return actual_filename
                            except Exception as rename_ex:
                                logger.error(f"❌ Failed to rename .part file: {rename_ex}")
                        
                        # Try to find any variant of the file (different extension)
                        possible_files = glob.glob(f"downloads/{video_id}.*")
                        possible_files = [f for f in possible_files if not f.endswith('.part')]
                        if possible_files:
                            found_file = possible_files[0]
                            logger.info(f"✅ Found alternative: {found_file}")
                            return found_file
                        
                        logger.error(f"❌ Download completed but file not found: {actual_filename}")
                        return None
                    except yt_dlp.utils.ExtractorError as ex:
                        error_msg = str(ex)
                        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                            logger.warning(
                                f"⚠️ YouTube bot detection for {video_id}. This is temporary.")
                        elif "not available" in error_msg.lower():
                            logger.error(
                                "❌ Video not available: May be region-blocked or private.")
                        elif "age" in error_msg.lower():
                            logger.error(
                                "❌ Age-restricted video: Cookies required.")
                        else:
                            logger.error("❌ YouTube extraction failed: %s", ex)
                        return None
                    except yt_dlp.utils.DownloadError as ex:
                        error_msg = str(ex)
                        if "416" in error_msg or "Requested range not satisfiable" in error_msg:
                            # HTTP 416 - file partially downloaded, delete and retry won't help
                            logger.warning(f"⚠️ Range error for {video_id}, skipping")
                        elif "failed to load cookies" in error_msg.lower() or "netscape format" in error_msg.lower():
                            logger.error(
                                "❌ Corrupted cookie file detected, removing: %s", cookie)
                            # Remove corrupted cookie from list and filesystem
                            if cookie and cookie in self.cookies:
                                self.cookies.remove(cookie)
                            try:
                                os.remove(f"HasiiMusic/cookies/{cookie}")
                            except:
                                pass
                        else:
                            logger.warning(f"⚠️ Download error for {video_id}: {ex}")
                        return None
                    except Exception as ex:
                        logger.warning(f"⚠️ Unexpected download error for {video_id}: {ex}")
                        return None

            # Run blocking download in thread pool to avoid blocking event loop
            return await asyncio.get_event_loop().run_in_executor(None, _download)
