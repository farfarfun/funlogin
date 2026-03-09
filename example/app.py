"""
funlogin 示例后端：挂载认证与绑定路由，并开启 CORS 供前端调用。
启动时自动创建数据库表（不依赖 Alembic）。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from funlogin import router
from funlogin.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="funlogin Example", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "funlogin example", "docs": "/docs", "api": "/api"}
