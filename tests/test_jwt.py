from funlogin.core.jwt import create_access_token, decode_token


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
