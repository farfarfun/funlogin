from urllib.parse import urlencode

from funlogin.config import get_settings


def get_authorize_url(redirect_uri: str, state: str) -> str:
    """构造 QQ 互联 OAuth2 授权页 URL。

    参数：
        redirect_uri: 授权成功后的回调地址，需与 QQ 互联后台配置一致。
        state: 防 CSRF 的随机状态串，回调时原样带回。

    返回：
        可直接跳转的 QQ 授权页完整 URL。
    """
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
    """用授权码换取 QQ 用户信息（access_token -> openid -> 用户资料，三步走）。

    参数：
        code: 授权回调携带的 code。
        redirect_uri: 与申请授权时一致的回调地址（QQ 互联要求换取 token 时携带）。
        _client: 测试用注入的 httpx 客户端，默认内部创建并自动关闭。

    返回：
        包含 ``openid``/``unionid``/``nickname``/``avatar`` 的字典；任一环节失败返回 ``None``。
    """
    import httpx

    settings = get_settings()
    client = _client or httpx.AsyncClient()
    try:
        # 第一步：用 code 换 access_token
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
        # QQ 互联返回的是文本格式：access_token=xxx&expires_in=7776000
        token = None
        for part in r.text.split("&"):
            if part.startswith("access_token="):
                token = part.split("=", 1)[1]
                break
        if not token:
            return None

        # 第二步：用 access_token 换 openid，返回格式为 JSONP：
        # callback( {"client_id":"xxx","openid":"xxx"} );
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

        # 第三步：用 openid + access_token 拉取用户资料
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
        avatar = (
            data.get("figureurl_qq_2")
            or data.get("figureurl_2")
            or data.get("figureurl", "")
        )

        return {
            "openid": openid,
            "unionid": data.get("unionid", ""),
            "nickname": nickname,
            "avatar": avatar,
        }
    finally:
        if _client is None:
            await client.aclose()
