import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from funlogin.auth.router import router
from funlogin.core.database import get_async_session


@pytest.mark.asyncio
async def test_register_and_login(db_session):
    app = FastAPI()
    app.include_router(router)

    async def get_test_session():
        yield db_session

    app.dependency_overrides[get_async_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        r = await ac.post(
            "/auth/register",
            json={"username": "testuser", "password": "pass123"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["code"] == 0
        assert "user_id" in data["data"]

        r2 = await ac.post(
            "/auth/login",
            json={"username": "testuser", "password": "pass123"},
        )
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["code"] == 0
        assert "access_token" in d2["data"]

        refresh_token = d2["data"]["refresh_token"]
        r3 = await ac.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert r3.status_code == 200
        d3 = r3.json()
        assert d3["code"] == 0
        assert "access_token" in d3["data"]


@pytest.mark.asyncio
async def test_register_duplicate_returns_400(db_session):
    from httpx import ASGITransport, AsyncClient
    from fastapi import FastAPI

    from funlogin.auth.router import router
    from funlogin.core.database import get_async_session

    app = FastAPI()
    app.include_router(router)
    async def get_test_session():
        yield db_session
    app.dependency_overrides[get_async_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        await ac.post("/auth/register", json={"username": "dup", "password": "p"})
        r = await ac.post("/auth/register", json={"username": "dup", "password": "q"})
        assert r.status_code == 400
