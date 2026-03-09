from funlogin.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "1"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_parses_sub():
    payload = {"sub": "123"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "123"
    assert "exp" in decoded


def test_create_refresh_token_returns_string():
    token = create_refresh_token({"sub": "1"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_rejects_expired():
    import time

    import jwt as pyjwt

    from funlogin.config import get_settings

    settings = get_settings()
    expired_payload = {"sub": "1", "exp": int(time.time()) - 3600}
    token = pyjwt.encode(
        expired_payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    decoded = decode_token(token)
    assert decoded is None
