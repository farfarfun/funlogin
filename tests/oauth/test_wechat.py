import pytest

from funlogin.oauth.wechat import exchange_code_for_user_info, get_authorize_url


def test_get_authorize_url():
    url = get_authorize_url("http://localhost/callback", "xyz")
    assert "open.weixin.qq.com" in url
    assert "state=xyz" in url
    assert "response_type=code" in url
    assert "scope=snsapi_userinfo" in url


class FakeResponse:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


@pytest.mark.asyncio
async def test_exchange_code_for_user_info():
    responses = iter(
        [
            FakeResponse({"access_token": "TOKEN", "openid": "OID123"}),
            FakeResponse({"nickname": "Test", "headimgurl": "https://avatar"}),
        ]
    )

    class FakeClient:
        async def get(self, url, **kwargs):
            return next(responses)

    result = await exchange_code_for_user_info("code", _client=FakeClient())

    assert result == {
        "openid": "OID123",
        "unionid": "",
        "nickname": "Test",
        "avatar": "https://avatar",
    }


@pytest.mark.asyncio
async def test_exchange_code_for_user_info_api_error():
    class FakeClient:
        async def get(self, url, **kwargs):
            return FakeResponse({"errcode": 40029})

    assert await exchange_code_for_user_info("code", _client=FakeClient()) is None
