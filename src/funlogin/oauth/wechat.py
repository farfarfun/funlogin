from urllib.parse import urlencode

from funlogin.config import get_settings


def get_authorize_url(redirect_uri: str, state: str) -> str:
    settings = get_settings()
    params = {
        "appid": settings.wechat_app_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "snsapi_userinfo",
        "state": state,
    }
    return f"https://open.weixin.qq.com/connect/oauth2/authorize?{urlencode(params)}#wechat_redirect"


async def exchange_code_for_user_info(code: str, *, _client=None) -> dict | None:
    import httpx

    settings = get_settings()
    client = _client or httpx.AsyncClient()
    try:
        # get access_token
        r = await client.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": settings.wechat_app_id,
                "secret": settings.wechat_app_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        if r.status_code != 200:
            return None
        data = r.json()
        if "errcode" in data:
            return None
        openid = data.get("openid", "")
        access_token = data.get("access_token", "")

        # get userinfo
        r2 = await client.get(
            "https://api.weixin.qq.com/sns/userinfo",
            params={"access_token": access_token, "openid": openid, "lang": "zh_CN"},
        )
        if r2.status_code != 200:
            return {
                "openid": openid,
                "unionid": data.get("unionid", ""),
                "nickname": "",
                "avatar": "",
            }
        u = r2.json()
        return {
            "openid": openid,
            "unionid": u.get("unionid", ""),
            "nickname": u.get("nickname", ""),
            "avatar": u.get("headimgurl", ""),
        }
    finally:
        if _client is None:
            await client.aclose()
