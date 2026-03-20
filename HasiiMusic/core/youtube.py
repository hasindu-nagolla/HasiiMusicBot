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
import glob
import time
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch
from HasiiMusic import config, logger
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
        self._max_video_height = getattr(config, "VIDEO_MAX_HEIGHT", 1080)

    def _locate_download_file(self, video_id: str, video: bool = False) -> Optional[str]:
        """Locate any completed download file for a video id."""
        pattern = f"downloads/{video_id}*"
        candidates = sorted([
            path for path in glob.glob(pattern)
            if not path.endswith((".part", ".ytdl", ".info.json", ".temp"))
        ])

        video_exts = {".mp4", ".mkv", ".webm", ".mov"}
        audio_exts = {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}

        if video:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in video_exts:
                    return path
        else:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in audio_exts:
                    return path

        for path in candidates:
            if os.path.isdir(path):
                continue
            return path
        return None

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

    def _is_bot_check_error(self, error_msg: str) -> bool:
        msg = (error_msg or "").lower()
        return (
            "sign in to confirm" in msg
            or "not a bot" in msg
            or "page needs to be reloaded" in msg
        )

    def _remove_cookie(self, cookie_path: Optional[str]) -> None:
        if not cookie_path:
            return
        cookie_name = os.path.basename(cookie_path)
        if cookie_name in self.cookies:
            self.cookies.remove(cookie_name)
        try:
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
        except Exception:
            pass

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
        current_time = asyncio.get_running_loop().time()

        if cache_key in self.search_cache:
            cached_result, cache_timestamp = self.search_cache[cache_key]
            if current_time - cache_timestamp < 600:  # 10 minutes
                # Return cached result with new message_id
                cached_result.message_id = m_id
                return cached_result

        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
        except Exception as e:
            logger.warning(f"⚠️ YouTube search failed for '{query}': {e}")
            return None

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

    async def download(self, video_id: str, is_live: bool = False, video: bool = False) -> Optional[str]:
        url = self.base + video_id

        # For live streams, extract the direct stream URL using yt-dlp with cookies
        if is_live:
            cookie = self.get_cookies()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie,
                "format": "bestaudio/best",
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # Use android client to bypass YouTube bot detection on server IPs
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            def _extract_url():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        return info.get("url") or info.get("manifest_url")
                    except yt_dlp.utils.ExtractorError as ex:
                        error_msg = str(ex)
                        if self._is_bot_check_error(error_msg) or "bot" in error_msg.lower():
                            logger.error(
                                "YouTube bot-check triggered for live stream. Rotating cookie.")
                            self._remove_cookie(cookie)
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
                            self._remove_cookie(cookie)
                        elif self._is_bot_check_error(error_msg):
                            logger.error("YouTube bot-check triggered for live stream. Rotating cookie.")
                            self._remove_cookie(cookie)
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

        # Download audio/video file
        # Don't hardcode extension - let yt-dlp choose best available format
        # Will use outtmpl pattern to get actual extension
        filename_pattern = f"downloads/{video_id}"
        
        # Check if any completed file for this video_id already exists
        existing_files = [
            f for f in glob.glob(f"{filename_pattern}.*")
            if not f.endswith('.part')
        ]
        if video:
            video_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}
            ]
            if video_candidates:
                return video_candidates[0]
        else:
            audio_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}
            ]
            if audio_candidates:
                return audio_candidates[0]
        
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
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # Use android client to bypass YouTube bot detection on server IPs.
                # Android client does not require PO tokens and works from datacenter IPs.
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            if video:
                # Video mode: download best video/audio combo up to configured height
                height_filter = ""
                if self._max_video_height and self._max_video_height > 0:
                    height_filter = f"[height<={self._max_video_height}]"
                format_chain = (
                    f"bestvideo[ext=mp4]{height_filter}+bestaudio[ext=m4a]/"
                    f"bestvideo{height_filter}+bestaudio/"
                    "bestvideo+bestaudio/best"
                )
                ydl_opts = {
                    **base_opts,
                    "format": format_chain,
                    "merge_output_format": "mp4",
                    "postprocessors": [
                        {
                            "key": "FFmpegVideoConvertor",
                            "preferedformat": "mp4",
                        }
                    ],
                }
            else:
                # Audio mode: favor m4a/opus for best compatibility
                ydl_opts = {
                    **base_opts,
                    "format": "bestaudio[ext=m4a]/bestaudio[acodec=opus]/bestaudio/best",
                    "postprocessors": [],
                }

            ydl_opts_no_cookie = {
                **ydl_opts,
            }
            ydl_opts_cookie = {
                **ydl_opts,
                "cookiefile": cookie,
            }

            last_error_kind = None

            def _download(ydl_runtime_opts):
                nonlocal last_error_kind
                ydl_instance = None
                try:
                    last_error_kind = None
                    ydl_instance = yt_dlp.YoutubeDL(ydl_runtime_opts)
                    # Extract info to get actual extension downloaded
                    info = ydl_instance.extract_info(url, download=True)
                    if not info:
                        logger.error(f"❌ Failed to extract info for {video_id}")
                        return None
                    
                    time.sleep(0.5)
                    located = self._locate_download_file(video_id, video=video)
                    if located:
                        return located
                    logger.error(f"❌ Download completed but file not found for: {video_id}")
                    return None
                except yt_dlp.utils.ExtractorError as ex:
                    error_msg = str(ex)
                    if self._is_bot_check_error(error_msg) or "bot" in error_msg.lower():
                        last_error_kind = "bot"
                        logger.warning(
                            f"⚠️ YouTube bot-check for {video_id}.")
                    elif "not available" in error_msg.lower():
                        last_error_kind = "availability"
                        logger.error(
                            "❌ Video not available: May be region-blocked or private.")
                    elif "age" in error_msg.lower():
                        last_error_kind = "age"
                        logger.error(
                            "❌ Age-restricted video: Cookies required.")
                    else:
                        last_error_kind = "extractor"
                        logger.error("❌ YouTube extraction failed: %s", ex)
                    return None
                except yt_dlp.utils.DownloadError as ex:
                    error_msg = str(ex)
                    recovered = self._locate_download_file(video_id, video=video)
                    if "unable to rename file" in error_msg.lower() and recovered:
                        logger.warning(
                            f"⚠️ Renaming failed for {video_id}, using recovered file {Path(recovered).name}"
                        )
                        return recovered
                    if "416" in error_msg or "Requested range not satisfiable" in error_msg:
                        last_error_kind = "range"
                        # HTTP 416 - file partially downloaded, delete and retry won't help
                        logger.warning(f"⚠️ Range error for {video_id}, skipping")
                    elif "failed to load cookies" in error_msg.lower() or "netscape format" in error_msg.lower():
                        last_error_kind = "cookie"
                        logger.warning(f"⚠️ Failed to load cookies for {video_id}: {error_msg}")
                        # Remove corrupted cookie from list and filesystem
                        self._remove_cookie(ydl_runtime_opts.get("cookiefile"))
                    elif self._is_bot_check_error(error_msg):
                        last_error_kind = "bot"
                        logger.warning(f"⚠️ Bot-check for {video_id}: {error_msg}")
                        self._remove_cookie(ydl_runtime_opts.get("cookiefile"))
                    else:
                        last_error_kind = "download"
                        logger.warning(f"⚠️ Download error for {video_id}: {ex}")
                        if recovered:
                            logger.warning(
                                f"⚠️ Using recovered file for {video_id} despite download error"
                            )
                            return recovered
                    return None
                except Exception as ex:
                    last_error_kind = "unexpected"
                    logger.warning(f"⚠️ Unexpected download error for {video_id}: {ex}")
                    return None
                finally:
                    # CRITICAL: Explicitly close yt-dlp to release file handles
                    if ydl_instance:
                        try:
                            ydl_instance.close()
                        except Exception:
                            pass

            # Attempt 1: with cookie (needed for age-restricted/private videos)
            primary_opts = ydl_opts_cookie if cookie else ydl_opts_no_cookie
            result = await asyncio.to_thread(_download, primary_opts)
            if result:
                return result

            # Bot-check mitigation from yt-dlp wiki: rotate/avoid stale cookies
            if last_error_kind in {"bot", "cookie"}:
                fresh_cookie = self.get_cookies()
                if fresh_cookie and fresh_cookie != cookie:
                    logger.info(f"🔄 Retrying {video_id} with rotated cookie...")
                    rotated_opts = {**ydl_opts_cookie, "cookiefile": fresh_cookie}
                    result = await asyncio.to_thread(_download, rotated_opts)
                    if result:
                        return result

                logger.info(f"🧪 Retrying {video_id} without cookies...")
                result = await asyncio.to_thread(_download, ydl_opts_no_cookie)
                if result:
                    return result

            return None
