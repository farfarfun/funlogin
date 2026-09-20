import time

# 进程内内存存储，仅用于开发/单实例场景；多实例部署需换成 Redis 等共享存储。
_store: dict[str, tuple[str, float]] = {}
_DEFAULT_TTL = 300  # 验证码默认有效期：5 分钟


def store_code(phone: str, code: str, ttl: int = _DEFAULT_TTL) -> None:
    """记录手机号对应的验证码及过期时间。

    参数：
        phone: 手机号。
        code: 验证码明文。
        ttl: 有效期（秒），默认 300 秒。
    """
    _store[phone] = (code, time.time() + ttl)


def get_and_verify_code(phone: str, code: str) -> bool:
    """校验验证码，命中（无论成功与否，只要未过期）后立即失效，防止重放。

    参数：
        phone: 手机号。
        code: 用户提交的验证码。

    返回：
        校验通过返回 ``True``，否则（未发送过、已过期、不匹配）返回 ``False``。
    """
    if phone not in _store:
        return False
    stored_code, expiry = _store[phone]
    if time.time() > expiry:
        del _store[phone]
        return False
    if stored_code != code:
        return False
    del _store[phone]
    return True


def clear_code(phone: str) -> None:
    """清除某手机号已记录的验证码（如需提前失效时调用）。"""
    _store.pop(phone, None)
