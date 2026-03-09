import pytest
from unittest.mock import AsyncMock, patch

from funlogin.oauth.qq import exchange_code_for_user_info, get_authorize_url


def test_get_authorize_url():
    url = get_authorize_url("http://localhost/callback", "xyz")
    assert "graph.qq.com" in url
    assert "state=xyz" in url
    assert "response_type=code" in url


@pytest.mark.asyncio
async def test_exchange_code_for_user_info_mock():
    responses = [
        ("access_token=TOKEN&expires_in=7776000", None),
        ('callback( {"openid":"OID123"} );', None),
        ('{"nickname":"Test","figureurl_qq_2":"https://avatar"}', {"nickname": "Test", "figureurl_qq_2": "https://avatar"}),
    ]
    idx = [0]

    async def fake_get(url, **kwargs):
        i = idx[0]
        idx[0] += 1
        txt, j = responses[min(i, 2)]
        class Resp:
            status_code = 200
            text = txt
            def json(s):
                return j or {}
        return Resp()

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.aclose = AsyncMock()

    with patch("httpx.AsyncClient") as MockClient:
        MockClient.return_value = mock_client
        result = await exchange_code_for_user_info("code", "http://localhost/cb")
        assert result is not None
        assert result["openid"] == "OID123"
        assert result["nickname"] == "Test"
