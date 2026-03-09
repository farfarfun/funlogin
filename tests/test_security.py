from funlogin.core.security import hash_password, verify_password


def test_hash_password_returns_not_plaintext():
    plain = "test"
    hashed = hash_password(plain)
    assert hashed != plain
    assert len(hashed) > 0


def test_verify_password_correct():
    plain = "test"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong():
    plain = "test"
    hashed = hash_password(plain)
    assert verify_password("wrong", hashed) is False
