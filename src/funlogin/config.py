from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class FunloginSettings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./funlogin.db"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire: int = 3600
    jwt_refresh_expire: int = 604800
    qq_app_id: str = ""
    qq_app_key: str = ""
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    aliyun_access_key: str = ""
    aliyun_secret: str = ""
    aliyun_sms_sign: str = ""
    aliyun_sms_template: str = ""

    model_config = SettingsConfigDict(env_prefix="FUNLOGIN_", env_file=".env")


@lru_cache
def get_settings() -> FunloginSettings:
    return FunloginSettings()
