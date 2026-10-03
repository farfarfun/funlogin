from funlogin.auth.repository import AuthRepository
from funlogin.core.jwt import create_access_token, create_refresh_token
from funlogin.core.security import hash_password, verify_password
from funlogin.sms.aliyun import verify_code


class AuthService:
    """认证业务逻辑：注册、登录（用户名/邮箱/手机号三种方式）与角色管理。

    依赖 :class:`AuthRepository` 完成数据访问，自身不直接操作数据库会话。
    """

    def __init__(self, repository: AuthRepository) -> None:
        """注入数据访问层。

        参数：
            repository: 封装用户/凭据表读写的仓储对象。
        """
        self.repo = repository

    async def register_with_username_password(
        self, username: str, password: str
    ) -> dict | None:
        """用用户名+密码注册新用户。

        参数：
            username: 用户名，需唯一。
            password: 明文密码，内部会哈希后存储。

        返回：
            成功返回 ``{"user_id": ...}``；用户名已存在返回 ``None``。
        """
        cred = await self.repo.get_credential_by_identifier("username", username)
        if cred is not None:
            return None
        user = await self.repo.create_user()
        await self.repo.create_credential(
            user_id=user.id,
            type="username",
            identifier=username,
            secret_hash=hash_password(password),
        )
        return {"user_id": user.id}

    async def login_with_username_password(
        self, username: str, password: str
    ) -> dict | None:
        """用用户名+密码登录。

        参数：
            username: 用户名。
            password: 明文密码，与存储的哈希比对。

        返回：
            成功返回 ``{"access_token": ..., "refresh_token": ...}``；
            用户名不存在或密码错误返回 ``None``。
        """
        cred = await self.repo.get_credential_by_identifier("username", username)
        if cred is None or not verify_password(password, cred.secret_hash):
            return None
        payload = {"sub": str(cred.user_id)}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
        }

    async def register_with_email_password(
        self, email: str, password: str
    ) -> dict | None:
        """用邮箱+密码注册新用户。

        参数：
            email: 邮箱地址，需唯一。
            password: 明文密码，内部会哈希后存储。

        返回：
            成功返回 ``{"user_id": ...}``；邮箱已存在返回 ``None``。
        """
        cred = await self.repo.get_credential_by_identifier("email", email)
        if cred is not None:
            return None
        user = await self.repo.create_user()
        await self.repo.create_credential(
            user_id=user.id,
            type="email",
            identifier=email,
            secret_hash=hash_password(password),
        )
        return {"user_id": user.id}

    async def login_with_email_password(self, email: str, password: str) -> dict | None:
        """用邮箱+密码登录。

        参数：
            email: 邮箱地址。
            password: 明文密码，与存储的哈希比对。

        返回：
            成功返回 ``{"access_token": ..., "refresh_token": ...}``；
            邮箱不存在或密码错误返回 ``None``。
        """
        cred = await self.repo.get_credential_by_identifier("email", email)
        if cred is None or not verify_password(password, cred.secret_hash):
            return None
        payload = {"sub": str(cred.user_id)}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
        }

    async def register_with_phone_code(self, phone: str, code: str) -> dict | None:
        """用手机号+短信验证码注册新用户。

        参数：
            phone: 手机号，需唯一。
            code: 短信验证码。

        返回：
            成功返回 ``{"user_id": ...}``；验证码错误或手机号已存在返回 ``None``。
        """
        if not verify_code(phone, code):
            return None
        cred = await self.repo.get_credential_by_identifier("phone", phone)
        if cred is not None:
            return None
        user = await self.repo.create_user()
        await self.repo.create_credential(
            user_id=user.id,
            type="phone",
            identifier=phone,
            secret_hash="",
        )
        return {"user_id": user.id}

    async def login_with_phone_code(self, phone: str, code: str) -> dict | None:
        """用手机号+短信验证码登录。

        参数：
            phone: 手机号。
            code: 短信验证码。

        返回：
            成功返回 ``{"access_token": ..., "refresh_token": ...}``；
            验证码错误或手机号未注册返回 ``None``。
        """
        if not verify_code(phone, code):
            return None
        cred = await self.repo.get_credential_by_identifier("phone", phone)
        if cred is None:
            return None
        payload = {"sub": str(cred.user_id)}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
        }

    async def update_role(self, user_id: int, role: int):
        """修改用户角色，枚举值由调用方自行定义。

        参数：
            user_id: 目标用户 ID。
            role: 新角色值。

        返回：
            更新后的 ``User`` 对象；用户不存在返回 ``None``。
        """
        return await self.repo.update_user_role(user_id, role)

    async def get_user_info(self, user_id: int) -> dict | None:
        """获取用户信息：user_id, role, username, email, phone, created_at, updated_at"""
        user = await self.repo.get_user_by_id(user_id)
        if user is None:
            return None
        creds = await self.repo.get_credentials_by_user_id(user_id)
        info = {
            "user_id": user.id,
            "role": user.role,
            "username": None,
            "email": None,
            "phone": None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        for c in creds:
            if c.type == "username":
                info["username"] = c.identifier
            elif c.type == "email":
                info["email"] = c.identifier
            elif c.type == "phone":
                info["phone"] = c.identifier
        return info
