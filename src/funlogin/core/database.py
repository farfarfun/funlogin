from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from funlogin.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """提供一个请求级异步数据库会话。

    返回：
        可供 FastAPI 依赖注入使用的 ``AsyncSession``；请求结束后自动关闭。
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """创建所有表（无需 Alembic 时在应用启动时调用）。"""
    import funlogin.models  # noqa: F401 — 注册模型到 Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
