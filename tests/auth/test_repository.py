import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from funlogin.core.database import Base
from funlogin.models import PhoneBinding, QQBinding, User, UserCredential, WeChatBinding


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


@pytest.fixture
def repo(db_session):
    from funlogin.auth.repository import AuthRepository

    return AuthRepository(db_session)


@pytest.mark.asyncio
async def test_create_user(repo):
    user = await repo.create_user()
    assert user is not None
    assert user.id > 0
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_get_user_by_id(repo):
    user = await repo.create_user()
    found = await repo.get_user_by_id(user.id)
    assert found is not None
    assert found.id == user.id
    assert (await repo.get_user_by_id(99999)) is None


@pytest.mark.asyncio
async def test_create_credential(repo):
    user = await repo.create_user()
    cred = await repo.create_credential(
        user_id=user.id,
        type="username",
        identifier="alice",
        secret_hash="hashed",
    )
    assert cred is not None
    assert cred.identifier == "alice"
    assert cred.type == "username"


@pytest.mark.asyncio
async def test_get_credential_by_identifier(repo):
    user = await repo.create_user()
    await repo.create_credential(
        user_id=user.id,
        type="username",
        identifier="bob",
        secret_hash="hash",
    )
    cred = await repo.get_credential_by_identifier("username", "bob")
    assert cred is not None
    assert cred.identifier == "bob"
    assert (await repo.get_credential_by_identifier("username", "nonexistent")) is None
