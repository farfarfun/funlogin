import pytest

from funlogin.auth.repository import AuthRepository
from funlogin.bind.repository import BindRepository
from funlogin.bind.service import BindService
from funlogin.sms.code_store import store_code


@pytest.fixture
def bind_service(db_session):
    return BindService(BindRepository(db_session))


@pytest.mark.asyncio
async def test_bind_phone(bind_service, db_session):
    user = await AuthRepository(db_session).create_user()
    store_code("13900001111", "1234")
    ok = await bind_service.bind_phone(user.id, "13900001111", "1234")
    assert ok is True
    bindings = await bind_service.list_bindings(user.id)
    assert "13900001111" in bindings["phone"]


@pytest.mark.asyncio
async def test_bind_qq(bind_service, db_session):
    user = await AuthRepository(db_session).create_user()
    ok = await bind_service.bind_qq(user.id, "qq_openid_1", nickname="QQUser")
    assert ok is True
    bindings = await bind_service.list_bindings(user.id)
    assert len(bindings["qq"]) == 1
    assert bindings["qq"][0]["nickname"] == "QQUser"


@pytest.mark.asyncio
async def test_bind_wechat(bind_service, db_session):
    user = await AuthRepository(db_session).create_user()
    ok = await bind_service.bind_wechat(user.id, "wx_openid_1", nickname="WxUser")
    assert ok is True
    bindings = await bind_service.list_bindings(user.id)
    assert len(bindings["wechat"]) == 1


@pytest.mark.asyncio
async def test_list_bindings(bind_service, db_session):
    user = await AuthRepository(db_session).create_user()
    store_code("13800138000", "9999")
    await bind_service.bind_phone(user.id, "13800138000", "9999")
    await bind_service.bind_qq(user.id, "oid", nickname="N")
    b = await bind_service.list_bindings(user.id)
    assert "13800138000" in b["phone"]
    assert len(b["qq"]) == 1
