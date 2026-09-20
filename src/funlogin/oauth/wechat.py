from urllib.parse import urlencode

from funlogin.config import get_settings


def get_authorize_url(redirect_uri: str, state: str) -> str:
    """构造微信开放平台 OAuth2 授权页 URL（网页应用 `snsapi_userinfo` 授权）。

    参数：
        redirect_uri: 授权成功后的回调地址，需与微信开放平台后台配置一致。
        state: 防 CSRF 的随机状态串，回调时原样带回。

    返回：
        可直接跳转的微信授权页完整 URL。
    """
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
    """用授权码换取微信用户信息（access_token -> 用户资料，两步走）。

    参数：
        code: 授权回调携带的 code。
        _client: 测试用注入的 httpx 客户端，默认内部创建并自动关闭。

    返回：
        包含 ``openid``/``unionid``/``nickname``/``avatar`` 的字典；换 token 失败返回 ``None``，
        用户资料拉取失败时仍返回带空昵称/头像的字典。
    """
    import httpx

    settings = get_settings()
    client = _client or httpx.AsyncClient()
    try:
        # 第一步：用 code 换 access_token + openid
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

        # 第二步：用 access_token + openid 拉取用户资料
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
