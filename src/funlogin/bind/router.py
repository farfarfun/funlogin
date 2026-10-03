import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from funlogin.bind.repository import BindRepository
from funlogin.bind.service import BindService
from funlogin.deps import get_current_user
from funlogin.models import User
from funlogin.oauth.qq import exchange_code_for_user_info as qq_exchange
from funlogin.oauth.qq import get_authorize_url as qq_authorize_url
from funlogin.oauth.wechat import exchange_code_for_user_info as wechat_exchange
from funlogin.oauth.wechat import get_authorize_url as wechat_authorize_url
from funlogin.sms.aliyun import send_sms_code
from funlogin.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/bind", tags=["bind"])


def get_bind_service(session: AsyncSession = Depends(get_async_session)) -> BindService:
    """FastAPI 依赖工厂：按请求创建绑定当前数据库会话的 ``BindService``。

    参数：
        session: 由 :func:`funlogin.core.database.get_async_session` 注入的异步会话。

    返回：
        新建的 ``BindService`` 实例。
    """
    return BindService(BindRepository(session))


class SendCodeRequest(BaseModel):
    phone: str


class BindPhoneRequest(BaseModel):
    phone: str
    code: str


@router.post("/phone/send-code")
async def send_phone_code(
    body: SendCodeRequest,
    user: User = Depends(get_current_user),
) -> dict:
    """向指定手机号发送绑定用验证码，需登录。

    参数：
        body: 请求体，包含 ``phone`` 手机号。
        user: 当前登录用户（仅用于鉴权，不参与发码逻辑）。

    返回：
        统一响应格式；短信发送失败时返回 500。
    """
    code = "".join(secrets.choice("0123456789") for _ in range(6))
    ok = send_sms_code(body.phone, code)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    return {"code": 0, "data": None, "message": "ok"}


@router.post("/phone")
async def bind_phone(
    body: BindPhoneRequest,
    user: User = Depends(get_current_user),
    service: BindService = Depends(get_bind_service),
) -> dict:
    """用短信验证码绑定手机号到当前用户，需登录。

    参数：
        body: 请求体，包含 ``phone``、``code``。
        user: 当前登录用户。
        service: 绑定业务服务。

    返回：
        统一响应格式；验证码错误或手机号已被其他用户绑定时返回 400。
    """
    ok = await service.bind_phone(user.id, body.phone, body.code)
    if not ok:
        raise HTTPException(
            status_code=400, detail="Invalid code or phone already bound"
        )
    return {"code": 0, "data": None, "message": "ok"}


@router.get("/qq/authorize")
async def qq_authorize(redirect_uri: str) -> dict:
    """生成 QQ 互联 OAuth2 授权页 URL 及防 CSRF 的 ``state``。

    参数：
        redirect_uri: 授权成功后的回调地址。

    返回：
        统一响应格式，``data`` 含 ``url``、``state``。
    """
    state = secrets.token_urlsafe(16)
    url = qq_authorize_url(redirect_uri, state)
    return {"code": 0, "data": {"url": url, "state": state}, "message": "ok"}


class BindQQRequest(BaseModel):
    code: str
    redirect_uri: str


@router.post("/qq/callback")
async def qq_callback(
    body: BindQQRequest,
    user: User = Depends(get_current_user),
    service: BindService = Depends(get_bind_service),
) -> dict:
    """用 QQ 授权回调的 code 换取用户信息并绑定到当前用户，需登录。

    参数：
        body: 请求体，包含 ``code``、``redirect_uri``。
        user: 当前登录用户。
        service: 绑定业务服务。

    返回：
        统一响应格式；QQ 授权失败或该 QQ 已绑定其他用户时返回 400。
    """
    info = await qq_exchange(body.code, body.redirect_uri)
    if info is None:
        raise HTTPException(status_code=400, detail="QQ auth failed")
    ok = await service.bind_qq(
        user.id,
        info["openid"],
        info.get("unionid", ""),
        info.get("nickname", ""),
        info.get("avatar", ""),
    )
    if not ok:
        raise HTTPException(status_code=400, detail="QQ already bound to another user")
    return {"code": 0, "data": None, "message": "ok"}


@router.get("/wechat/authorize")
async def wechat_authorize(redirect_uri: str) -> dict:
    """生成微信开放平台 OAuth2 授权页 URL 及防 CSRF 的 ``state``。

    参数：
        redirect_uri: 授权成功后的回调地址。

    返回：
        统一响应格式，``data`` 含 ``url``、``state``。
    """
    state = secrets.token_urlsafe(16)
    url = wechat_authorize_url(redirect_uri, state)
    return {"code": 0, "data": {"url": url, "state": state}, "message": "ok"}


class BindWeChatRequest(BaseModel):
    code: str


@router.post("/wechat/callback")
async def wechat_callback(
    body: BindWeChatRequest,
    user: User = Depends(get_current_user),
    service: BindService = Depends(get_bind_service),
) -> dict:
    """用微信授权回调的 code 换取用户信息并绑定到当前用户，需登录。

    参数：
        body: 请求体，包含 ``code``。
        user: 当前登录用户。
        service: 绑定业务服务。

    返回：
        统一响应格式；微信授权失败或该微信已绑定其他用户时返回 400。
    """
    info = await wechat_exchange(body.code)
    if info is None:
        raise HTTPException(status_code=400, detail="WeChat auth failed")
    ok = await service.bind_wechat(
        user.id,
        info["openid"],
        info.get("unionid", ""),
        info.get("nickname", ""),
        info.get("avatar", ""),
    )
    if not ok:
        raise HTTPException(
            status_code=400, detail="WeChat already bound to another user"
        )
    return {"code": 0, "data": None, "message": "ok"}


@router.get("/list")
async def list_bindings(
    user: User = Depends(get_current_user),
    service: BindService = Depends(get_bind_service),
) -> dict:
    """查询当前用户已绑定的手机号、QQ、微信列表，需登录。

    参数：
        user: 当前登录用户。
        service: 绑定业务服务。

    返回：
        统一响应格式，``data`` 为 ``{"phone": [...], "qq": [...], "wechat": [...]}``。
    """
    data = await service.list_bindings(user.id)
    return {"code": 0, "data": data, "message": "ok"}
