from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.models import User, UserCredential


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self) -> User:
        user = User()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_credential(
        self,
        user_id: int,
        type: str,
        identifier: str,
        secret_hash: str = "",
    ) -> UserCredential:
        cred = UserCredential(
            user_id=user_id,
            type=type,
            identifier=identifier,
            secret_hash=secret_hash,
        )
        self.session.add(cred)
        await self.session.commit()
        await self.session.refresh(cred)
        return cred

    async def update_user_role(self, user_id: int, role: int) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user is None:
            return None
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_credentials_by_user_id(self, user_id: int) -> list[UserCredential]:
        result = await self.session.execute(
            select(UserCredential).where(UserCredential.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_credential_by_identifier(
        self, type: str, identifier: str
    ) -> UserCredential | None:
        result = await self.session.execute(
            select(UserCredential).where(
                UserCredential.type == type,
                UserCredential.identifier == identifier,
            )
        )
        return result.scalar_one_or_none()
