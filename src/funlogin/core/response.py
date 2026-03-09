from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def success(data=None, message: str = "ok") -> dict:
    return {"code": 0, "data": data, "message": message}


def fail(code: int, message: str, data=None) -> dict:
    return {"code": code, "data": data, "message": message}


def setup_exception_handlers(app: FastAPI) -> None:
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
