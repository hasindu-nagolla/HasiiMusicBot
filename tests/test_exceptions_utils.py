import pytest

from HasiiMusic.utils import exceptions


def test_is_ignored_error_by_keyword():
    err = Exception("Nᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ in chat")
    assert exceptions.is_ignored_error(err) is True


def test_is_ignored_error_negative():
    err = RuntimeError("unexpected failure")
    assert exceptions.is_ignored_error(err) is False


def test_assistant_err_inherits_exception():
    with pytest.raises(exceptions.AssistantErr) as exc:
        raise exceptions.AssistantErr("boom")
    assert "boom" in str(exc.value)
