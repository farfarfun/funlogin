from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class FunloginSettings(BaseSettings):
    """funlogin 运行配置，字段均可通过环境变量（前缀 ``FUNLOGIN_``）或 ``.env`` 覆盖。

    出于安全考虑，``jwt_secret`` 没有默认值：未配置时启动会直接失败，
    避免生产环境意外使用一个所有部署都相同的固定密钥签发 JWT。
    """

    database_url: str = "sqlite+aiosqlite:///./funlogin.db"
    jwt_secret: str
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
