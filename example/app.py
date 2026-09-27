"""兼容入口；生产环境请使用已安装包的 ``funlogin.app:app``。"""

from funlogin.app import app, root

__all__ = ["app", "root"]
