from funlogin.config import get_settings
from funlogin.sms.code_store import get_and_verify_code, store_code


def send_sms_code(phone: str, code: str) -> bool:
    settings = get_settings()
    if not settings.aliyun_access_key or not settings.aliyun_secret:
        store_code(phone, code)
        return True
    try:
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_dysmsapi20170525 import models as dysms_models
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
        return False


def verify_code(phone: str, code: str) -> bool:
    return get_and_verify_code(phone, code)
