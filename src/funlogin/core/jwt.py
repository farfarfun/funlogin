import time
from typing import Any

import jwt as pyjwt

from funlogin.config import get_settings


def create_access_token(payload: dict[str, Any]) -> str:
    """创建访问令牌。

    参数：
        payload: 将写入令牌的声明；原字典不会被修改。

    返回：
        使用当前 JWT 配置签发的访问令牌字符串。
    """
    settings = get_settings()
    payload = dict(payload)
    payload["exp"] = int(time.time()) + settings.jwt_access_expire
    return pyjwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(payload: dict[str, Any]) -> str:
    """创建刷新令牌。

    参数：
        payload: 将写入令牌的声明；原字典不会被修改。

    返回：
        使用当前 JWT 配置签发的刷新令牌字符串。
    """
    settings = get_settings()
    payload = dict(payload)
    payload["exp"] = int(time.time()) + settings.jwt_refresh_expire
    return pyjwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """验证并解析 JWT。

    参数：
        token: 待验证的 JWT 字符串。

    返回：
        验证成功返回令牌声明；令牌非法或过期返回 ``None``。
    """
    settings = get_settings()
    try:
        return pyjwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except pyjwt.PyJWTError:
        return None
