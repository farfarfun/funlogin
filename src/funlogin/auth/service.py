from funlogin.auth.repository import AuthRepository
from funlogin.core.jwt import create_access_token, create_refresh_token
from funlogin.core.security import hash_password, verify_password
from funlogin.sms.aliyun import verify_code


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repo = repository

    async def register_with_username_password(
        self, username: str, password: str
    ) -> dict | None:
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

    async def login_with_email_password(
        self, email: str, password: str
    ) -> dict | None:
        cred = await self.repo.get_credential_by_identifier("email", email)
        if cred is None or not verify_password(password, cred.secret_hash):
            return None
        payload = {"sub": str(cred.user_id)}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
        }

    async def register_with_phone_code(
        self, phone: str, code: str
    ) -> dict | None:
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
