from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.models import User, UserCredential


class AuthRepository:
    """用户与登录凭据表的数据访问层，不含业务规则（业务判断在 :class:`AuthService`）。"""

    def __init__(self, session: AsyncSession) -> None:
        """绑定一个数据库会话，所有方法复用同一事务上下文。

        参数：
            session: SQLAlchemy 异步会话。
        """
        self.session = session

    async def create_user(self) -> User:
        """创建一条空的 ``User`` 记录（具体登录方式由后续 ``create_credential`` 关联）。

        返回：
            已写入并刷新的 ``User`` 对象。
        """
        user = User()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """按主键查询用户。

        参数：
            user_id: 用户 ID。

        返回：
            找到返回 ``User``，否则返回 ``None``。
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_credential(
        self,
        user_id: int,
        type: str,
        identifier: str,
        secret_hash: str = "",
    ) -> UserCredential:
        """创建一条登录凭据记录。

        参数：
            user_id: 所属用户 ID。
            type: 凭据类型（``"username"``/``"email"``/``"phone"``）。
            identifier: 登录标识（用户名/邮箱/手机号）。
            secret_hash: 密码哈希；手机号验证码登录无密码时留空。

        返回：
            已写入并刷新的 ``UserCredential`` 对象。
        """
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
        """更新用户角色。

        参数：
            user_id: 用户 ID。
            role: 新角色值。

        返回：
            更新后的 ``User``；用户不存在返回 ``None``。
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return None
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_credentials_by_user_id(self, user_id: int) -> list[UserCredential]:
        """查询用户的全部登录凭据。

        参数：
            user_id: 用户 ID。

        返回：
            该用户名下的 ``UserCredential`` 列表，无记录时为空列表。
        """
        result = await self.session.execute(
            select(UserCredential).where(UserCredential.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_credential_by_identifier(
        self, type: str, identifier: str
    ) -> UserCredential | None:
        """按类型+标识查询登录凭据（用于判重与登录校验）。

        参数：
            type: 凭据类型（``"username"``/``"email"``/``"phone"``）。
            identifier: 登录标识。

        返回：
            找到返回 ``UserCredential``，否则返回 ``None``。
        """
        result = await self.session.execute(
            select(UserCredential).where(
                UserCredential.type == type,
                UserCredential.identifier == identifier,
            )
        )
        return result.scalar_one_or_none()
