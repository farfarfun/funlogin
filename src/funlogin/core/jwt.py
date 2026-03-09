import time

import jwt as pyjwt

from funlogin.config import get_settings


def create_access_token(payload: dict) -> str:
    settings = get_settings()
    payload = dict(payload)
    payload["exp"] = int(time.time()) + settings.jwt_access_expire
    return pyjwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(payload: dict) -> str:
    settings = get_settings()
    payload = dict(payload)
    payload["exp"] = int(time.time()) + settings.jwt_refresh_expire
    return pyjwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return pyjwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except pyjwt.PyJWTError:
        return None
