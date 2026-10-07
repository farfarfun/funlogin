from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
import pytest

from funlogin.core.response import setup_exception_handlers


@pytest.mark.asyncio
async def test_exception_handler_returns_documented_response_format():
    app = FastAPI()
    setup_exception_handlers(app)

    @app.get("/protected")
    async def protected() -> None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {
        "code": 40101,
        "data": None,
        "message": "Not authenticated",
    }
