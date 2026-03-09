import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from funlogin.auth.repository import AuthRepository
from funlogin.auth.service import AuthService
from funlogin.bind.router import router as bind_router
from funlogin.core.database import get_async_session
from funlogin.core.jwt import create_access_token
from funlogin.sms.code_store import store_code


@pytest.mark.asyncio
async def test_list_bindings_requires_auth(db_session):
    app = FastAPI()
    app.include_router(bind_router)

    async def get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        r = await ac.get("/bind/list")
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_bindings_with_token(db_session):
    app = FastAPI()
    app.include_router(bind_router)

    async def get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = get_session

    user = await AuthRepository(db_session).create_user()
    token = create_access_token({"sub": str(user.id)})

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        r = await ac.get(
            "/bind/list",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert r.json()["code"] == 0
        assert "phone" in r.json()["data"]


@pytest.mark.asyncio
async def test_bind_phone_flow(db_session):
    app = FastAPI()
    app.include_router(bind_router)

    async def get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = get_session

    user = await AuthRepository(db_session).create_user()
    token = create_access_token({"sub": str(user.id)})
    store_code("13900000001", "888888")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        r = await ac.post(
            "/bind/phone",
            json={"phone": "13900000001", "code": "888888"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        r2 = await ac.get("/bind/list", headers={"Authorization": f"Bearer {token}"})
        assert "13900000001" in r2.json()["data"]["phone"]
