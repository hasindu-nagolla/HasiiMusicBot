import asyncio

import pytest

from HasiiMusic.utils import sys as sys_utils


def test_bot_sys_stats(monkeypatch):
    # Freeze uptime at 10 seconds for a deterministic result
    monkeypatch.setattr(sys_utils, "_boot_", 100)
    monkeypatch.setattr(sys_utils.time, "time", lambda: 110)

    monkeypatch.setattr(sys_utils.psutil, "cpu_percent", lambda interval=None: 12.5)
    monkeypatch.setattr(sys_utils.psutil, "virtual_memory", lambda: type("vm", (), {"percent": 34.0})())
    monkeypatch.setattr(sys_utils.psutil, "disk_usage", lambda path: type("du", (), {"percent": 56.0})())

    uptime, cpu, ram, disk = asyncio.run(sys_utils.bot_sys_stats())
    assert uptime == "10s"
    assert cpu == "12.5%"
    assert ram == "34.0%"
    assert disk == "56.0%"
