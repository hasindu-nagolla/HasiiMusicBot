import asyncio

import pytest

from HasiiMusic.utils import formatters


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, ""),
        (59, "59s"),
        (61, "1ᴍ:1s"),
        (3661, "1ʜ:1ᴍ:1s"),
    ],
)
def test_get_readable_time(seconds, expected):
    assert formatters.get_readable_time(seconds) == expected


@pytest.mark.parametrize(
    "size, expected",
    [
        (0, ""),
        (500, "500.00  B"),
        (2048, "2.00 KiB"),
    ],
)
def test_convert_bytes(size, expected):
    assert formatters.convert_bytes(size) == expected


def test_int_to_alpha_and_back():
    numeric_id = 109
    alpha_id = asyncio.run(formatters.int_to_alpha(numeric_id))
    assert alpha_id == "baj"
    recovered = asyncio.run(formatters.alpha_to_int(alpha_id))
    assert recovered == numeric_id


@pytest.mark.parametrize(
    "time_str, expected",
    [
        ("45", 45),
        ("01:01", 61),
        ("01:02:03", 3723),
    ],
)
def test_time_to_seconds(time_str, expected):
    assert formatters.time_to_seconds(time_str) == expected


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (None, "-"),
        (9, "00:09"),
        (75, "01:15"),
        (3661, "01:01:01"),
        (90061, "01:01:01:01"),
    ],
)
def test_seconds_to_min(seconds, expected):
    assert formatters.seconds_to_min(seconds) == expected


@pytest.mark.parametrize(
    "seconds, speed, expected_format, expected_total",
    [
        (120, "0.5", "04:00", 240),
        (120, "0.75", "03:00", 180),
        (120, "1.5", "01:30", 90),
        (120, "2.0", "01:00", 60),
    ],
)
def test_speed_converter_adjustments(seconds, speed, expected_format, expected_total):
    formatted, total = formatters.speed_converter(seconds, speed)
    assert formatted == expected_format
    assert total == expected_total


def test_speed_converter_invalid():
    assert formatters.speed_converter(None, "1.0") == "-"
