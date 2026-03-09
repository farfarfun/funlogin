import time
from typing import Optional

# In-memory store for development. Use Redis in production.
_store: dict[str, tuple[str, float]] = {}
_DEFAULT_TTL = 300  # 5 minutes


def store_code(phone: str, code: str, ttl: int = _DEFAULT_TTL) -> None:
    _store[phone] = (code, time.time() + ttl)


def get_and_verify_code(phone: str, code: str) -> bool:
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
    _store.pop(phone, None)
