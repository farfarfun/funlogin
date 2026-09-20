from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "ok") -> dict:
    """构造统一成功响应体 ``{"code": 0, "data": ..., "message": ...}``。

    参数：
        data: 业务数据，任意可 JSON 序列化对象。
        message: 提示信息，默认 ``"ok"``。

    返回：
        统一响应格式的字典。
    """
    return {"code": 0, "data": data, "message": message}


def fail(code: int, message: str, data: Any = None) -> dict:
    """构造统一失败响应体 ``{"code": ..., "data": ..., "message": ...}``。

    参数：
        code: 业务错误码（非 0）。
        message: 错误说明。
        data: 附加数据，默认 ``None``。

    返回：
        统一响应格式的字典。
    """
    return {"code": code, "data": data, "message": message}


def setup_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册统一异常处理器，把 ``HTTPException`` 转成统一响应格式。

    参数：
        app: 待注册处理器的 FastAPI 应用实例。
    """
    from fastapi import HTTPException

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code = 40001
        if exc.status_code == 401:
            code = 40101
        elif exc.status_code == 403:
            code = 40301
        elif exc.status_code >= 500:
            code = 50001
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": code, "data": None, "message": exc.detail},
        )
