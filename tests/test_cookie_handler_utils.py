from HasiiMusic.utils import cookie_handler


def test_extract_paste_id_variants():
    assert cookie_handler._extract_paste_id("https://example.com/path/abc/") == "abc"
    assert cookie_handler._extract_paste_id("https://example.com") == ""


def test_resolve_raw_cookie_url_passthrough():
    url = "https://example.com/mycookie"
    assert cookie_handler.resolve_raw_cookie_url(url) == url
    assert cookie_handler.resolve_raw_cookie_url("") == ""


def test_resolve_raw_cookie_url_known_services():
    pastebin_url = "https://pastebin.com/ABC123"
    batbin_url = "https://batbin.me/xyz789"
    assert cookie_handler.resolve_raw_cookie_url(pastebin_url) == "https://pastebin.com/raw/ABC123"
    assert cookie_handler.resolve_raw_cookie_url(batbin_url) == "https://batbin.me/raw/xyz789"
