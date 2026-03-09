from fastapi import APIRouter

from funlogin.auth.router import router as auth_router
from funlogin.bind.router import router as bind_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(bind_router)
