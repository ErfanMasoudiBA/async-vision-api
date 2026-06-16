from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.read_write_file import router as read_write_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["System and health"])
api_router.include_router(read_write_router, tags=["File Management"])
