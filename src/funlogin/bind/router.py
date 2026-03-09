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
):
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
):
    ok = await service.bind_phone(user.id, body.phone, body.code)
    if not ok:
        raise HTTPException(
            status_code=400, detail="Invalid code or phone already bound"
        )
    return {"code": 0, "data": None, "message": "ok"}


@router.get("/qq/authorize")
async def qq_authorize(redirect_uri: str):
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
):
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
async def wechat_authorize(redirect_uri: str):
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
):
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
):
    data = await service.list_bindings(user.id)
    return {"code": 0, "data": data, "message": "ok"}
