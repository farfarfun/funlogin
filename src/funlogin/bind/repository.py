from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.models import PhoneBinding, QQBinding, WeChatBinding


class BindRepository:
    """手机号/QQ/微信绑定表的数据访问层，不含业务规则（业务判断在 :class:`BindService`）。"""

    def __init__(self, session: AsyncSession) -> None:
        """绑定一个数据库会话，所有方法复用同一事务上下文。

        参数：
            session: SQLAlchemy 异步会话。
        """
        self.session = session

    async def create_phone_binding(self, user_id: int, phone: str) -> PhoneBinding:
        """创建手机号绑定记录。

        参数：
            user_id: 用户 ID。
            phone: 手机号。

        返回：
            已写入并刷新的 ``PhoneBinding`` 对象。
        """
        b = PhoneBinding(user_id=user_id, phone=phone)
        self.session.add(b)
        await self.session.commit()
        await self.session.refresh(b)
        return b

    async def create_qq_binding(
        self,
        user_id: int,
        openid: str,
        unionid: str = "",
        nickname: str = "",
        avatar_url: str = "",
    ) -> QQBinding:
        """创建 QQ 绑定记录。

        参数：
            user_id: 用户 ID。
            openid: QQ 用户唯一标识。
            unionid: QQ 互联 unionid，可能为空。
            nickname: QQ 昵称，可能为空。
            avatar_url: QQ 头像地址，可能为空。

        返回：
            已写入并刷新的 ``QQBinding`` 对象。
        """
        b = QQBinding(
            user_id=user_id,
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url,
        )
        self.session.add(b)
        await self.session.commit()
        await self.session.refresh(b)
        return b

    async def create_wechat_binding(
        self,
        user_id: int,
        openid: str,
        unionid: str = "",
        nickname: str = "",
        avatar_url: str = "",
    ) -> WeChatBinding:
        """创建微信绑定记录。

        参数：
            user_id: 用户 ID。
            openid: 微信用户唯一标识。
            unionid: 微信开放平台 unionid，可能为空。
            nickname: 微信昵称，可能为空。
            avatar_url: 微信头像地址，可能为空。

        返回：
            已写入并刷新的 ``WeChatBinding`` 对象。
        """
        b = WeChatBinding(
            user_id=user_id,
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url,
        )
        self.session.add(b)
        await self.session.commit()
        await self.session.refresh(b)
        return b

    async def get_phone_binding(self, phone: str) -> PhoneBinding | None:
        """按手机号查询绑定记录（用于判断该手机号是否已被占用）。

        参数：
            phone: 手机号。

        返回：
            找到返回 ``PhoneBinding``，否则返回 ``None``。
        """
        r = await self.session.execute(
            select(PhoneBinding).where(PhoneBinding.phone == phone)
        )
        return r.scalar_one_or_none()

    async def get_qq_binding(self, openid: str) -> QQBinding | None:
        """按 openid 查询 QQ 绑定记录（用于判断该账号是否已被占用）。

        参数：
            openid: QQ 用户唯一标识。

        返回：
            找到返回 ``QQBinding``，否则返回 ``None``。
        """
        r = await self.session.execute(
            select(QQBinding).where(QQBinding.openid == openid)
        )
        return r.scalar_one_or_none()

    async def get_wechat_binding(self, openid: str) -> WeChatBinding | None:
        """按 openid 查询微信绑定记录（用于判断该账号是否已被占用）。

        参数：
            openid: 微信用户唯一标识。

        返回：
            找到返回 ``WeChatBinding``，否则返回 ``None``。
        """
        r = await self.session.execute(
            select(WeChatBinding).where(WeChatBinding.openid == openid)
        )
        return r.scalar_one_or_none()

    async def list_bindings(self, user_id: int) -> dict:
        """查询指定用户的手机号、QQ、微信绑定列表。

        参数：
            user_id: 用户 ID。

        返回：
            ``{"phone": [...], "qq": [...], "wechat": [...]}``，无绑定时对应列表为空。
        """
        phones = await self.session.execute(
            select(PhoneBinding).where(PhoneBinding.user_id == user_id)
        )
        qqs = await self.session.execute(
            select(QQBinding).where(QQBinding.user_id == user_id)
        )
        wechats = await self.session.execute(
            select(WeChatBinding).where(WeChatBinding.user_id == user_id)
        )
        return {
            "phone": [p.phone for p in phones.scalars().all()],
            "qq": [
                {"openid": q.openid, "nickname": q.nickname}
                for q in qqs.scalars().all()
            ],
            "wechat": [
                {"openid": w.openid, "nickname": w.nickname}
                for w in wechats.scalars().all()
            ],
        }
