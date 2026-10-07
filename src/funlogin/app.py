"""funlogin 正式 ASGI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from funlogin import router
from funlogin.config import get_settings
from funlogin.core.database import init_db
from funlogin.core.response import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库。"""
    await init_db()
    yield


app = FastAPI(title="funlogin", version="1.0.10", lifespan=lifespan)
setup_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    # 默认只放行本机回环地址，生产跨域来源通过 FUNLOGIN_CORS_ORIGINS 显式配置，
    # 不默认开放通配符 + allow_credentials 的不受限生产访问策略。
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    """返回服务健康信息和文档地址。"""
    return {"message": "funlogin", "docs": "/docs", "api": "/api"}
