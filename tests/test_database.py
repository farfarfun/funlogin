import pytest
from funlogin.core.database import engine, AsyncSessionLocal, get_async_session


def test_engine_created():
    assert engine is not None


def test_async_session_local_created():
    assert AsyncSessionLocal is not None


@pytest.mark.asyncio
async def test_get_async_session_yields_session():
    session = None
    async for s in get_async_session():
        session = s
        break
    assert session is not None
