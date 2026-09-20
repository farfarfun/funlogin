from farlog import getLogger

from funlogin.config import get_settings
from funlogin.sms.code_store import get_and_verify_code, store_code

logger = getLogger("funlogin")


def _mask_phone(phone: str) -> str:
    """日志里只保留手机号首尾，避免明文记录用户 PII。"""
    if len(phone) <= 4:
        return "***"
    return f"{phone[:3]}***{phone[-2:]}"


def send_sms_code(phone: str, code: str) -> bool:
    """通过阿里云短信服务发送验证码（未配置阿里云凭据时降级为仅本地存码，便于开发环境联调）。

    参数：
        phone: 接收验证码的手机号。
        code: 验证码明文，由调用方生成。

    返回：
        发送（或本地降级存码）成功返回 ``True``；调用阿里云 API 失败返回 ``False``。
    """
    settings = get_settings()
    if not settings.aliyun_access_key or not settings.aliyun_secret:
        store_code(phone, code)
        return True
    try:
        from alibabacloud_dysmsapi20170525 import models as dysms_models
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_tea_openapi import models as openapi_models

        config = openapi_models.Config(
            access_key_id=settings.aliyun_access_key,
            access_key_secret=settings.aliyun_secret,
            endpoint="dysmsapi.aliyuncs.com",
        )
        client = Client(config)
        req = dysms_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=settings.aliyun_sms_sign,
            template_code=settings.aliyun_sms_template,
            template_param=f'{{"code":"{code}"}}',
        )
        client.send_sms(req)
        store_code(phone, code)
        return True
    except Exception:
        # 阿里云 SDK 的异常类型较杂（网络错误、TeaException 等），这里统一兜底，
        # 但必须保留上下文（手机号脱敏、短信签名/模板）便于定位，
        # 不能像之前那样直接吞掉；logger.exception 会自带完整 traceback。
        logger.exception(  # noqa: PLE1205 — farlog/loguru 用 `{}` 占位，不是 stdlib logging 的 %s
            "阿里云短信发送失败: phone={} sign={} template={}",
            _mask_phone(phone),
            settings.aliyun_sms_sign,
            settings.aliyun_sms_template,
        )
        return False


def verify_code(phone: str, code: str) -> bool:
    """校验短信验证码，参见 :func:`funlogin.sms.code_store.get_and_verify_code`。

    参数：
        phone: 手机号。
        code: 用户提交的验证码。

    返回：
        校验通过返回 ``True``，否则返回 ``False``。
    """
    return get_and_verify_code(phone, code)
