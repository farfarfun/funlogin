from funlogin.config import get_settings


def test_get_settings_returns_settings():
    s = get_settings()
    assert s is not None
    assert hasattr(s, "database_url")
