# ==============================================================================
# youtube.py - YouTube Integration
# ==============================================================================
# Handles searching for tracks, downloading them via yt-dlp, and managing cookies.
# ==============================================================================

import os
import re
import glob
import time
import yt_dlp
import random
import asyncio
import aiohttp
from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from HasiiMusic import config, logger
from HasiiMusic.helpers import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="  # Base YouTube URL
        self.cookies = []  # List of available cookie files
        self.checked = False  # Whether cookies directory has been checked
        self.warned = False  # Whether missing cookies warning has been shown

        # Match YouTube URLs
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

        # Cache results for 10 mins
        self.search_cache = {}  # {"query_video": (result, timestamp)}
        self.cache_time = {}  # Deprecated, using tuple in search_cache instead

        # Limit concurrent downloads to prevent lag
        self._download_semaphore = asyncio.Semaphore(5)  # Max 5 simultaneous downloads
        self._max_video_height = getattr(config, "VIDEO_MAX_HEIGHT", 1080)

    def _locate_download_file(self, video_id: str, video: bool = False) -> Optional[str]:
        pattern = f"downloads/{video_id}*"
        candidates = sorted([
            path for path in glob.glob(pattern)
            if not path.endswith((".part", ".ytdl", ".info.json", ".temp"))
        ])

        video_exts = {".mp4", ".mkv", ".mov"}
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
                            # Update cookie list
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"✅ Saved: {cookie_filename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Cookie download error from {url}: {e}")
        
        # Refresh cookie list
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
        # Check cache (10 min TTL)
        cache_key = query
        current_time = asyncio.get_running_loop().time()

        if cache_key in self.search_cache:
            cached_result, cache_timestamp = self.search_cache[cache_key]
            if current_time - cache_timestamp < 600:  # 10 minutes
                # Return a fresh copy
                fresh = replace(cached_result)
                fresh.message_id = m_id
                fresh.file_path = None
                fresh.user = None
                fresh.time = 0
                fresh.video = False
                return fresh

        try:
            is_url = bool(re.match(r"https?://", query))
            if self.valid(query) or (is_url and "soundcloud.com" in query):
                def _extract():
                    cookie = self.get_cookies() if self.checked else None
                    ydl_opts = {
                        "quiet": True,
                        "noplaylist": True,
                        "extract_flat": "in_playlist",
                        "cookiefile": cookie
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(query, download=False)

                data = await asyncio.to_thread(_extract)
                if not data:
                    return None

                duration_sec = data.get("duration")
                is_live = data.get("is_live", False)
                if duration_sec is None and is_live:
                    duration = "LIVE"
                    duration_sec = 0
                else:
                    duration = utils.format_duration(int(duration_sec)) if duration_sec else "0:00"

                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("uploader") or data.get("channel", ""),
                    duration=duration,
                    duration_sec=int(duration_sec) if duration_sec else 0,
                    message_id=m_id,
                    title=(data.get("title") or "")[:25],
                    thumbnail=data.get("thumbnail") or "",
                    url=data.get("webpage_url") or query,
                    view_count=str(data.get("view_count", "")),
                    is_live=is_live,
                )
            else:
                def _extract_search():
                    cookie = self.get_cookies() if self.checked else None
                    ydl_opts = {
                        "quiet": True,
                        "extract_flat": True,
                        "cookiefile": cookie
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(f"ytsearch1:{query}", download=False)
                        
                results = await asyncio.to_thread(_extract_search)
                
                if not results or "entries" not in results or not results["entries"]:
                    return None
                    
                data = results["entries"][0]
                duration_sec = data.get("duration")
                is_live = data.get("is_live", False)
                if duration_sec is None and is_live:
                    duration = "LIVE"
                    duration_sec = 0
                else:
                    duration = utils.format_duration(int(duration_sec)) if duration_sec else "0:00"

                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("uploader") or data.get("channel", ""),
                    duration=duration,
                    duration_sec=int(duration_sec) if duration_sec else 0,
                    message_id=m_id,
                    title=(data.get("title") or "")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0] if data.get("thumbnails") else "",
                    url=data.get("url") or data.get("webpage_url") or f"https://youtube.com/watch?v={data.get('id')}",
                    view_count=str(data.get("view_count", "")),
                    is_live=is_live,
                )

            # Cache result (max 100)
            self.search_cache[cache_key] = (track, current_time)
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(),
                                 key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]

            return replace(track)
            
        except Exception as e:
            logger.warning(f"⚠️ YouTube search failed for '{query}': {e}")
            return None

    async def playlist(self, limit: int, user: str, url: str) -> list[Track]:
        try:
            is_url = bool(re.match(r"https?://", url))
            if self.valid(url) or (is_url and "soundcloud.com" in url):
                def _extract_playlist():
                    cookie = self.get_cookies() if self.checked else None
                    ydl_opts = {
                        "quiet": True,
                        "extract_flat": "in_playlist",
                        "cookiefile": cookie
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(url, download=False)
                        
            plist = await asyncio.to_thread(_extract_playlist)
            tracks = []

            # Check for videos
            if not plist or "entries" not in plist or not plist["entries"]:
                return []

            for data in plist["entries"][:limit]:
                try:
                    duration_sec = data.get("duration")
                    is_live = data.get("is_live", False)
                    if duration_sec is None and is_live:
                        duration = "LIVE"
                        duration_sec = 0
                    else:
                        duration = utils.format_duration(int(duration_sec)) if duration_sec else "0:00"

                    track = Track(
                        id=data.get("id", ""),
                        channel_name=data.get("uploader") or data.get("channel", ""),
                        duration=duration,
                        duration_sec=int(duration_sec) if duration_sec else 0,
                        title=(data.get("title", "Unknown")[:25]),
                        thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0] if data.get("thumbnails") else "",
                        url=data.get("url") or data.get("webpage_url") or f"https://youtube.com/watch?v={data.get('id')}",
                        user=user,
                        view_count="",
                    )
                    tracks.append(track)
                except Exception as e:
                    # Skip broken tracks
                    continue

            return tracks
        except Exception as e:
            logger.warning(f"⚠️ YouTube playlist extraction failed for '{url}': {e}")
            return []

    async def download(self, video_id: str, is_live: bool = False, video: bool = False) -> Optional[str]:
        url = self.base + video_id

        # Extract live stream URL
        if is_live:
            cookie = self.get_cookies()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie,
                "format": "bestaudio/best",
                "noplaylist": True,
                "socket_timeout": 20,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # Use android client to bypass YouTube bot detection on server IPs
                # "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            def _extract_url():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        if not info:
                            return None

                        direct = info.get("url")
                        if direct:
                            return direct

                        # Find URL in formats
                        for fmt in info.get("formats", []):
                            if fmt.get("acodec") != "none" and fmt.get("url"):
                                return fmt["url"]

                        return info.get("manifest_url")
                    except yt_dlp.utils.ExtractorError as ex:
                        error_msg = str(ex)
                        if "not available" in error_msg.lower():
                            logger.error(
                                "Video format not available or region-blocked.")
                        else:
                            logger.error(
                                "Live stream URL extraction failed: %s", ex)
                        return None
                    except Exception as ex:
                        logger.error(
                            "Unexpected error during live stream extraction: %s", ex)
                        return None

            try:
                stream_url = await asyncio.wait_for(asyncio.to_thread(_extract_url), timeout=35)
            except asyncio.TimeoutError:
                logger.error("Live stream URL extraction timed out for %s", video_id)
                return None

            return stream_url

        # Let yt-dlp choose the best format
        filename_pattern = f"downloads/{video_id}"
        
        # Check existing files
        existing_files = [
            f for f in glob.glob(f"{filename_pattern}.*")
            if not f.endswith('.part')
        ]
        if video:
            # NOTE: .webm excluded — audio downloads from /play produce .webm
            # which are audio-only. Only trust .mp4/.mkv/.mov as cached video.
            video_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".mov"}
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

            # Fallback to mp4 for audio
            container_fallbacks = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".mov"}
            ]
            if container_fallbacks:
                return container_fallbacks[0]
        
        # Create downloads dir
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
                # Max 4 fragments for stability
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 524288,  # 512KB chunks
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                # Android client bypass
                # "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            if video:
                # Download best video
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
                # Download best audio
                ydl_opts = {
                    **base_opts,
                    # "format": "bestaudio[ext=m4a]/bestaudio[acodec=opus]/bestaudio/best",
                    "format": "bestaudio/best",
                    "postprocessors": [],
                }

            ydl_opts_cookie = {
                **ydl_opts,
                "cookiefile": cookie,
            }

            def _download(ydl_runtime_opts):
                ydl_instance = None
                try:
                    ydl_instance = yt_dlp.YoutubeDL(ydl_runtime_opts)
                    # Extract info
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
                    if "not available" in error_msg.lower():
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
                    recovered = self._locate_download_file(video_id, video=video)
                    if "unable to rename file" in error_msg.lower() and recovered:
                        logger.warning(
                            f"⚠️ Renaming failed for {video_id}, using recovered file {Path(recovered).name}"
                        )
                        return recovered
                    if "416" in error_msg or "Requested range not satisfiable" in error_msg:
                        # HTTP 416 range error
                        logger.warning(f"⚠️ Range error for {video_id}, skipping")
                    else:
                        logger.warning(f"⚠️ Download error for {video_id}: {ex}")
                        if recovered:
                            logger.warning(
                                f"⚠️ Using recovered file for {video_id} despite download error"
                            )
                            return recovered
                    return None
                except Exception as ex:
                    logger.warning(f"⚠️ Unexpected download error for {video_id}: {ex}")
                    return None
                finally:
                    # Close yt-dlp safely
                    if ydl_instance:
                        try:
                            ydl_instance.close()
                        except Exception:
                            pass

            # Start download thread
            return await asyncio.to_thread(_download, ydl_opts_cookie)
