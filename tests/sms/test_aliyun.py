from funlogin.config import FunloginSettings
from funlogin.sms import aliyun
from funlogin.sms.aliyun import send_sms_code, verify_code
from funlogin.sms.code_store import clear_code, store_code


def test_send_sms_code_requires_credentials_by_default(monkeypatch):
    monkeypatch.setattr(aliyun, "get_settings", lambda: FunloginSettings(
        jwt_secret="test-secret"
    ))
    clear_code("13800138000")
    assert send_sms_code("13800138000", "123456") is False
    assert verify_code("13800138000", "123456") is False


def test_send_sms_code_stores_in_explicit_local_mode(monkeypatch):
    monkeypatch.setattr(aliyun, "get_settings", lambda: FunloginSettings(
        jwt_secret="test-secret", sms_local_mode=True
    ))
    clear_code("13800138000")
    assert send_sms_code("13800138000", "123456") is True
    assert verify_code("13800138000", "123456") is True


def test_verify_code_wrong_fails():
    store_code("13800138001", "654321")
    assert verify_code("13800138001", "111111") is False


def test_verify_code_removes_after_use():
    store_code("13800138002", "888888")
    assert verify_code("13800138002", "888888") is True
    assert verify_code("13800138002", "888888") is False  # already consumed
