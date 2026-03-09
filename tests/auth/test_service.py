import pytest

from funlogin.auth.repository import AuthRepository
from funlogin.auth.service import AuthService


@pytest.fixture
def auth_service(db_session):
    repo = AuthRepository(db_session)
    return AuthService(repo)


@pytest.mark.asyncio
async def test_register_with_username_password_success(auth_service):
    result = await auth_service.register_with_username_password(
        username="alice", password="secret123"
    )
    assert result is not None
    assert result.get("user_id") is not None
    assert result.get("user_id") > 0


@pytest.mark.asyncio
async def test_register_duplicate_username_fails(auth_service):
    await auth_service.register_with_username_password(username="bob", password="pass")
    result = await auth_service.register_with_username_password(
        username="bob", password="other"
    )
    assert result is None


@pytest.mark.asyncio
async def test_login_success_returns_tokens(auth_service):
    await auth_service.register_with_username_password(
        username="charlie", password="mypass"
    )
    result = await auth_service.login_with_username_password(
        username="charlie", password="mypass"
    )
    assert result is not None
    assert "access_token" in result
    assert "refresh_token" in result


@pytest.mark.asyncio
async def test_register_and_login_email(auth_service):
    result = await auth_service.register_with_email_password(
        email="alice@example.com", password="pass123"
    )
    assert result is not None
    login_result = await auth_service.login_with_email_password(
        email="alice@example.com", password="pass123"
    )
    assert login_result is not None
    assert "access_token" in login_result


@pytest.mark.asyncio
async def test_register_and_login_phone(auth_service, db_session):
    from funlogin.sms.code_store import store_code

    store_code("13900139000", "123456")
    result = await auth_service.register_with_phone_code("13900139000", "123456")
    assert result is not None
    store_code("13900139000", "654321")  # new code for login
    login_result = await auth_service.login_with_phone_code("13900139000", "654321")
    assert login_result is not None
    assert "access_token" in login_result


@pytest.mark.asyncio
async def test_login_wrong_password_fails(auth_service):
    await auth_service.register_with_username_password(
        username="dave", password="correct"
    )
    result = await auth_service.login_with_username_password(
        username="dave", password="wrong"
    )
    assert result is None
