import bcrypt


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码。

    参数：
        password: 待哈希的明文密码。

    返回：
        可持久化保存的 bcrypt 密码哈希。
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否与 bcrypt 哈希匹配。

    参数：
        plain_password: 待校验的明文密码。
        hashed_password: 已保存的 bcrypt 密码哈希。

    返回：
        密码匹配返回 ``True``，否则返回 ``False``。
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
