from funlogin.bind.repository import BindRepository
from funlogin.sms.aliyun import verify_code


class BindService:
    """第三方账号/手机号绑定业务逻辑：手机号、QQ、微信绑定与查询。

    依赖 :class:`BindRepository` 完成数据访问，自身不直接操作数据库会话。
    """

    def __init__(self, repository: BindRepository) -> None:
        """注入数据访问层。

        参数：
            repository: 封装绑定关系表读写的仓储对象。
        """
        self.repo = repository

    async def bind_phone(self, user_id: int, phone: str, code: str) -> bool:
        """绑定手机号，需先通过短信验证码校验。

        参数：
            user_id: 发起绑定的用户 ID。
            phone: 待绑定手机号。
            code: 短信验证码。

        返回：
            验证码正确且该手机号未被其他用户占用（或已绑定给同一用户）返回
            ``True``；验证码错误或手机号已被其他用户绑定返回 ``False``。
        """
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
        """绑定 QQ 账号（已通过 OAuth 换取的用户信息）。

        参数：
            user_id: 发起绑定的用户 ID。
            openid: QQ 返回的用户唯一标识。
            unionid: QQ 互联 unionid，可能为空。
            nickname: QQ 昵称，可能为空。
            avatar_url: QQ 头像地址，可能为空。

        返回：
            该 ``openid`` 未被其他用户占用（或已绑定给同一用户）返回
            ``True``；已被其他用户绑定返回 ``False``。
        """
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
        """绑定微信账号（已通过 OAuth 换取的用户信息）。

        参数：
            user_id: 发起绑定的用户 ID。
            openid: 微信返回的用户唯一标识。
            unionid: 微信开放平台 unionid，可能为空。
            nickname: 微信昵称，可能为空。
            avatar_url: 微信头像地址，可能为空。

        返回：
            该 ``openid`` 未被其他用户占用（或已绑定给同一用户）返回
            ``True``；已被其他用户绑定返回 ``False``。
        """
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
        """查询指定用户已绑定的手机号、QQ、微信列表。

        参数：
            user_id: 目标用户 ID。

        返回：
            ``{"phone": [...], "qq": [...], "wechat": [...]}``，无绑定时对应列表为空。
        """
        return await self.repo.list_bindings(user_id)
