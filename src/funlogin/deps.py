from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from funlogin.auth.repository import AuthRepository
from funlogin.core.database import get_async_session
from funlogin.core.jwt import decode_token
from funlogin.models import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    creds: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(creds.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await AuthRepository(session).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
