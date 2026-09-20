import os

# funlogin.config.FunloginSettings.jwt_secret 故意没有默认值（见 config.py），
# 生产环境缺失时必须启动失败。测试环境在此提供一个仅供测试使用的固定值，
# 必须在任何 `funlogin` 子模块被 import（进而触发 get_settings()）之前设置。
os.environ.setdefault(
    "FUNLOGIN_JWT_SECRET", "test-only-secret-do-not-use-in-production"
)

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from funlogin.core.database import Base
from funlogin.models import (  # noqa: F401 — 触发注册，供 Base.metadata.create_all 使用
    PhoneBinding,
    QQBinding,
    User,
    UserCredential,
    WeChatBinding,
)


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session
    await engine.dispose()
