import asyncio
import importlib

from HasiiMusic.utils import tuning


def test_max_concurrent_relation():
    assert tuning.MAX_CONCURRENT == min(64, tuning.CPU * 8)
    assert tuning.CHUNK_SIZE == 64 * 1024
    assert tuning.YTDLP_TIMEOUT == 30
    assert isinstance(tuning.SEM, asyncio.Semaphore)


def test_reload_respects_cpu_count(monkeypatch):
    monkeypatch.setattr("os.cpu_count", lambda: 2)
    module = importlib.reload(tuning)
    assert module.CPU == 2
    assert module.MAX_CONCURRENT == 16
    monkeypatch.undo()
    importlib.reload(tuning)
