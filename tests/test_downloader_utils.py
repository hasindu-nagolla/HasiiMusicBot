import os
import importlib

import pytest

from HasiiMusic.utils import downloader


@pytest.mark.parametrize(
    "link, expected",
    [
        ("", ""),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share", "dQw4w9WgXcQ"),
        ("https://example.com/watch", ""),
    ],
)
def test_extract_video_id(link, expected):
    assert downloader.extract_video_id(link) == expected


def test_get_cookie_file(tmp_path, monkeypatch):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("valid", encoding="utf-8")
    monkeypatch.setattr(downloader, "_COOKIES_FILE", str(cookie_file))
    assert downloader.get_cookie_file() == str(cookie_file)


def test_get_cookie_file_missing(monkeypatch, tmp_path):
    missing = tmp_path / "missing.txt"
    monkeypatch.setattr(downloader, "_COOKIES_FILE", str(missing))
    assert downloader.get_cookie_file() is None


def test_find_cached_file(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    cached = download_dir / "abc123.mp3"
    cached.write_text("data", encoding="utf-8")
    monkeypatch.setattr(downloader, "DOWNLOAD_DIR", str(download_dir))
    assert downloader.find_cached_file("abc123") == str(cached)
    assert downloader.find_cached_file("") is None


def test_get_ytdlp_base_opts_includes_cookie(monkeypatch):
    monkeypatch.setattr(downloader, "get_cookie_file", lambda: "cookiefile.txt")
    opts = downloader.get_ytdlp_base_opts()
    assert opts["cookiefile"] == "cookiefile.txt"


def test_get_ytdlp_base_opts_defaults(monkeypatch):
    monkeypatch.setattr(downloader, "get_cookie_file", lambda: None)
    opts = downloader.get_ytdlp_base_opts()
    assert opts["outtmpl"].endswith("%(id)s.%(ext)s")
    assert opts["cachedir"] == str(downloader.CACHE_DIR)
    assert opts["noplaylist"] is True


def test_log_download_source(monkeypatch):
    messages = []

    class DummyLogger:
        def info(self, msg):
            messages.append(msg)

    monkeypatch.setattr(downloader, "LOGGER", DummyLogger())
    downloader.log_download_source("Song", "YouTube")
    assert messages == ["Track 'Song' - Downloaded by YouTube"]
