from funlogin.bind.repository import BindRepository
from funlogin.sms.aliyun import verify_code


class BindService:
    def __init__(self, repository: BindRepository) -> None:
        self.repo = repository

    async def bind_phone(self, user_id: int, phone: str, code: str) -> bool:
        if not verify_code(phone, code):
            return False
        existing = await self.repo.get_phone_binding(phone)
        if existing and existing.user_id != user_id:
            return False
        if existing:
            return True  # already bound to same user
        await self.repo.create_phone_binding(user_id, phone)
        return True

    async def bind_qq(
        self,
        user_id: int,
        openid: str,
        unionid: str = "",
        nickname: str = "",
        avatar_url: str = "",
    ) -> bool:
        existing = await self.repo.get_qq_binding(openid)
        if existing and existing.user_id != user_id:
            return False
        if existing:
            return True
        await self.repo.create_qq_binding(
            user_id, openid, unionid, nickname, avatar_url
        )
        return True

    async def bind_wechat(
        self,
        user_id: int,
        openid: str,
        unionid: str = "",
        nickname: str = "",
        avatar_url: str = "",
    ) -> bool:
        existing = await self.repo.get_wechat_binding(openid)
        if existing and existing.user_id != user_id:
            return False
        if existing:
            return True
        await self.repo.create_wechat_binding(
            user_id, openid, unionid, nickname, avatar_url
        )
        return True

    async def list_bindings(self, user_id: int) -> dict:
        return await self.repo.list_bindings(user_id)
