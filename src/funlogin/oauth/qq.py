from urllib.parse import urlencode

from funlogin.config import get_settings


def get_authorize_url(redirect_uri: str, state: str) -> str:
    settings = get_settings()
    params = {
        "response_type": "code",
        "client_id": settings.qq_app_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "get_user_info",
    }
    return f"https://graph.qq.com/oauth2.0/authorize?{urlencode(params)}"


async def exchange_code_for_user_info(
    code: str, redirect_uri: str, *, _client=None
) -> dict | None:
    import httpx

    settings = get_settings()
    client = _client or httpx.AsyncClient()
    try:
        # get access_token
        r = await client.get(
            "https://graph.qq.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": settings.qq_app_id,
                "client_secret": settings.qq_app_key,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        if r.status_code != 200:
            return None
        # QQ returns text like access_token=xxx&expires_in=7776000
        token = None
        for part in r.text.split("&"):
            if part.startswith("access_token="):
                token = part.split("=", 1)[1]
                break
        if not token:
            return None

        # get openid - Returns: callback( {"client_id":"xxx","openid":"xxx"} );
        r2 = await client.get(
            "https://graph.qq.com/oauth2.0/me",
            params={"access_token": token},
        )
        if r2.status_code != 200:
            return None
        import json
        import re

        m = re.search(r"callback\s*\(\s*(\{.*?\})\s*\)", r2.text, re.DOTALL)
        if not m:
            return None
        me_data = json.loads(m.group(1))
        openid = me_data.get("openid")
        if not openid:
            return None

        # get user_info
        r3 = await client.get(
            "https://graph.qq.com/user/get_user_info",
            params={
                "access_token": token,
                "oauth_consumer_key": settings.qq_app_id,
                "openid": openid,
            },
        )
        if r3.status_code != 200:
            return {"openid": openid, "unionid": "", "nickname": "", "avatar": ""}
        data = r3.json()
        nickname = data.get("nickname", "")
        avatar = data.get("figureurl_qq_2") or data.get("figureurl_2") or data.get("figureurl", "")

        return {
            "openid": openid,
            "unionid": data.get("unionid", ""),
            "nickname": nickname,
            "avatar": avatar,
        }
    finally:
        if _client is None:
            await client.aclose()
