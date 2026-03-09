from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.models import PhoneBinding, QQBinding, WeChatBinding


class BindRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_phone_binding(self, user_id: int, phone: str) -> PhoneBinding:
        b = PhoneBinding(user_id=user_id, phone=phone)
        self.session.add(b)
        await self.session.commit()
        await self.session.refresh(b)
        return b

    async def create_qq_binding(
        self, user_id: int, openid: str, unionid: str = "", nickname: str = "", avatar_url: str = ""
    ) -> QQBinding:
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
        self, user_id: int, openid: str, unionid: str = "", nickname: str = "", avatar_url: str = ""
    ) -> WeChatBinding:
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
        r = await self.session.execute(
            select(PhoneBinding).where(PhoneBinding.phone == phone)
        )
        return r.scalar_one_or_none()

    async def get_qq_binding(self, openid: str) -> QQBinding | None:
        r = await self.session.execute(
            select(QQBinding).where(QQBinding.openid == openid)
        )
        return r.scalar_one_or_none()

    async def get_wechat_binding(self, openid: str) -> WeChatBinding | None:
        r = await self.session.execute(
            select(WeChatBinding).where(WeChatBinding.openid == openid)
        )
        return r.scalar_one_or_none()

    async def list_bindings(self, user_id: int) -> dict:
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
            "qq": [{"openid": q.openid, "nickname": q.nickname} for q in qqs.scalars().all()],
            "wechat": [{"openid": w.openid, "nickname": w.nickname} for w in wechats.scalars().all()],
        }
