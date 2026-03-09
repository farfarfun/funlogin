from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.auth.repository import AuthRepository
from funlogin.auth.service import AuthService
from funlogin.core.database import get_async_session
from funlogin.core.jwt import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(AuthRepository(session))


@router.post("/register")
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.register_with_username_password(
        username=body.username, password=body.password
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"code": 0, "data": result, "message": "ok"}


@router.post("/login")
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.login_with_username_password(
        username=body.username, password=body.password
    )
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
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
