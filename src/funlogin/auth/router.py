import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.auth.repository import AuthRepository
from funlogin.auth.service import AuthService
from funlogin.core.database import get_async_session
from funlogin.core.jwt import create_access_token, create_refresh_token, decode_token
from funlogin.sms.aliyun import send_sms_code

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    password: str | None = None
    code: str | None = None


class LoginRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    password: str | None = None
    code: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class SendCodeRequest(BaseModel):
    phone: str


@router.post("/send-code")
async def send_code(body: SendCodeRequest):
    code = "".join(secrets.choice("0123456789") for _ in range(6))
    ok = send_sms_code(body.phone, code)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    return {"code": 0, "data": None, "message": "ok"}


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(AuthRepository(session))


@router.post("/register")
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    if body.username and body.password:
        result = await service.register_with_username_password(
            username=body.username, password=body.password
        )
        if result is None:
            raise HTTPException(status_code=400, detail="Username already exists")
    elif body.email and body.password:
        result = await service.register_with_email_password(
            email=body.email, password=body.password
        )
        if result is None:
            raise HTTPException(status_code=400, detail="Email already exists")
    elif body.phone and body.code:
        result = await service.register_with_phone_code(
            phone=body.phone, code=body.code
        )
        if result is None:
            raise HTTPException(status_code=400, detail="Invalid code or phone already exists")
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide (username,password) or (email,password) or (phone,code)",
        )
    return {"code": 0, "data": result, "message": "ok"}


@router.post("/login")
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    if body.username and body.password:
        result = await service.login_with_username_password(
            username=body.username, password=body.password
        )
    elif body.email and body.password:
        result = await service.login_with_email_password(
            email=body.email, password=body.password
        )
    elif body.phone and body.code:
        result = await service.login_with_phone_code(
            phone=body.phone, code=body.code
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide (username,password) or (email,password) or (phone,code)",
        )
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"code": 0, "data": result, "message": "ok"}


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    tokens = {
        "access_token": create_access_token({"sub": sub}),
        "refresh_token": create_refresh_token({"sub": sub}),
    }
    return {"code": 0, "data": tokens, "message": "ok"}
