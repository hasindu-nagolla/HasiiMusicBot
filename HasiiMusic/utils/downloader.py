import asyncio
import contextlib
import os
import re
from functools import partial
from glob import glob
from typing import Dict, Iterable, Optional, Union

import aiofiles
import aiohttp
from aiohttp import TCPConnector
from yt_dlp import YoutubeDL

from HasiiMusic.core.dir import DOWNLOAD_DIR as _DOWNLOAD_DIR, CACHE_DIR
from HasiiMusic.utils.cookie_handler import COOKIE_PATH
from HasiiMusic.utils.tuning import CHUNK_SIZE, SEM
from config import (
    API_KEY,
    API_URL,
    YTDLP_AUDIO_FORMAT,
    YTDLP_PREFERRED_AUDIO_BITRATE,
    YTDLP_VIDEO_FORMAT,
)

USE_API: bool = bool(API_URL and API_KEY)

_COOKIES_FILE = str(COOKIE_PATH)

_inflight: Dict[str, asyncio.Future] = {}
_inflight_lock = asyncio.Lock()

_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


def extract_video_id(link: str) -> str:
    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]
    return link.split("/")[-1].split("?")[0]


def _cookiefile_path() -> Optional[str]:
    try:
        if _COOKIES_FILE and os.path.exists(_COOKIES_FILE) and os.path.getsize(
            _COOKIES_FILE
        ) > 0:
            return _COOKIES_FILE
    except Exception:
        pass
    return None


_DEFAULT_AUDIO_EXTS: tuple[str, ...] = ("mp3", "m4a", "webm", "opus", "mka")
_DEFAULT_VIDEO_EXTS: tuple[str, ...] = ("mp4", "mkv", "webm", "mov")


def _find_downloaded_file(
    video_id: str,
    *,
    preferred_exts: Optional[Iterable[str]] = None,
    expected_ext: Optional[str] = None,
) -> Optional[str]:
    base = f"{_DOWNLOAD_DIR}/{video_id}"
    order: list[str] = []

    def _append(ext: Optional[str]) -> None:
        if not ext:
            return
        ext = ext.lstrip(".").lower()
        if ext and ext not in order:
            order.append(ext)

    if preferred_exts:
        for ext in preferred_exts:
            _append(ext)
    _append(expected_ext)

    for ext in order:
        candidate = f"{base}.{ext}"
        if os.path.exists(candidate):
            return candidate

    for path in glob(f"{base}.*"):
        if os.path.exists(path):
            return path

    return None


def file_exists(video_id: str) -> Optional[str]:
    return _find_downloaded_file(video_id, preferred_exts=_DEFAULT_AUDIO_EXTS)


def _safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]+', "_", (name or "").strip())[:200]


def _ytdlp_base_opts() -> Dict[str, Union[str, int, bool]]:
    opts: Dict[str, Union[str, int, bool]] = {
        "outtmpl": f"{_DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "overwrites": True,
        "continuedl": True,
        "noprogress": True,
        "concurrent_fragment_downloads": 16,
        "http_chunk_size": 1 << 20,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        "cachedir": str(CACHE_DIR),
        "prefer_ffmpeg": True,
    }
    cookiefile = _cookiefile_path()
    if cookiefile:
        opts["cookiefile"] = cookiefile
    return opts


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session
    async with _session_lock:
        if _session and not _session.closed:
            return _session
        timeout = aiohttp.ClientTimeout(
            total=600, sock_connect=20, sock_read=60)
        connector = TCPConnector(
            limit=0, ttl_dns_cache=300, enable_cleanup_closed=True)
        _session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return _session


async def api_download_song(link: str) -> Optional[str]:
    if not USE_API:
        return None
    vid = extract_video_id(link)
    poll_url = f"{API_URL}/song/{vid}?api={API_KEY}"
    try:
        session = await _get_session()
        while True:
            async with session.get(poll_url) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                s = str(data.get("status", "")).lower()
                if s == "downloading":
                    await asyncio.sleep(1.5)
                    continue
                if s != "done":
                    return None
                dl = data.get("link")
                fmt = str(data.get("format", "mp3")).lower()
                out_path = f"{_DOWNLOAD_DIR}/{vid}.{fmt}"
                async with session.get(dl) as fr:
                    if fr.status != 200:
                        return None
                    async with aiofiles.open(out_path, "wb") as f:
                        async for chunk in fr.content.iter_chunked(CHUNK_SIZE):
                            if not chunk:
                                break
                            await f.write(chunk)
                return out_path
    except Exception:
        return None


def _download_ytdlp(
    link: str,
    opts: Dict,
    *,
    preferred_exts: Optional[Iterable[str]] = None,
) -> Optional[str]:
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
            vid = info.get("id")
            if not vid:
                ydl.download([link])
                return None

            expected_ext = str(info.get("ext") or "").lower() or None
            existing = _find_downloaded_file(
                vid, preferred_exts=preferred_exts, expected_ext=expected_ext
            )
            if existing:
                return existing

            ydl.download([link])
            return _find_downloaded_file(
                vid, preferred_exts=preferred_exts, expected_ext=expected_ext
            )
    except Exception:
        return None


async def _with_sem(coro):
    async with SEM:
        return await coro


async def _dedup(key: str, runner):
    async with _inflight_lock:
        fut = _inflight.get(key)
        if fut:
            return await fut
        fut = asyncio.get_running_loop().create_future()
        _inflight[key] = fut
    try:
        res = await runner()
        fut.set_result(res)
        return res
    except Exception:
        fut.set_result(None)
        return None
    finally:
        async with _inflight_lock:
            _inflight.pop(key, None)


async def yt_dlp_download(
    link: str, type: str, format_id: str = None, title: str = None
) -> Optional[str]:
    loop = asyncio.get_running_loop()

    if type == "audio":
        key = f"a:{link}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update({"format": YTDLP_AUDIO_FORMAT})
            bitrate = YTDLP_PREFERRED_AUDIO_BITRATE
            if bitrate.isdigit():
                opts.setdefault("postprocessors", []).append(
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate,
                    }
                )
            return await _with_sem(
                loop.run_in_executor(
                    None,
                    partial(
                        _download_ytdlp,
                        link,
                        opts,
                        preferred_exts=_DEFAULT_AUDIO_EXTS,
                    ),
                )
            )

        return await _dedup(key, run)

    if type == "video":
        key = f"v:{link}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update({"format": YTDLP_VIDEO_FORMAT})
            return await _with_sem(
                loop.run_in_executor(
                    None,
                    partial(
                        _download_ytdlp,
                        link,
                        opts,
                        preferred_exts=_DEFAULT_VIDEO_EXTS,
                    ),
                )
            )

        return await _dedup(key, run)

    if type == "song_video" and format_id and title:
        safe_title = _safe_filename(title)
        key = f"sv:{link}:{format_id}:{safe_title}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update(
                {
                    "format": f"{format_id}+140",
                    "outtmpl": f"{_DOWNLOAD_DIR}/{safe_title}.mp4",
                    "prefer_ffmpeg": True,
                    "merge_output_format": "mp4",
                }
            )
            await _with_sem(
                loop.run_in_executor(
                    None, lambda: YoutubeDL(opts).download([link]))
            )
            return f"{_DOWNLOAD_DIR}/{safe_title}.mp4"

        return await _dedup(key, run)

    if type == "song_audio" and format_id and title:
        safe_title = _safe_filename(title)
        key = f"sa:{link}:{format_id}:{safe_title}"

        async def run():
            opts = _ytdlp_base_opts()
            opts.update(
                {
                    "format": format_id,
                    "outtmpl": f"{_DOWNLOAD_DIR}/{safe_title}.%(ext)s",
                    "prefer_ffmpeg": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
            await _with_sem(
                loop.run_in_executor(
                    None, lambda: YoutubeDL(opts).download([link]))
            )
            return f"{_DOWNLOAD_DIR}/{safe_title}.mp3"

        return await _dedup(key, run)

    return None


async def download_audio_concurrent(link: str) -> Optional[str]:
    vid = extract_video_id(link)
    cached = file_exists(vid)
    if cached:
        return cached

    if not USE_API:
        return await yt_dlp_download(link, type="audio")

    key = f"rac:{link}"

    async def run():
        yt_task = asyncio.create_task(yt_dlp_download(link, type="audio"))
        api_task = asyncio.create_task(api_download_song(link))
        done, pending = await asyncio.wait(
            {yt_task, api_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for t in done:
            with contextlib.suppress(Exception):
                res = t.result()
                if res:
                    for p in pending:
                        p.cancel()
                        with contextlib.suppress(Exception, asyncio.CancelledError):
                            await p
                    return res
        for t in pending:
            with contextlib.suppress(Exception, asyncio.CancelledError):
                res = await t
                if res:
                    return res
        return None

    return await _dedup(key, lambda: _with_sem(run()))
