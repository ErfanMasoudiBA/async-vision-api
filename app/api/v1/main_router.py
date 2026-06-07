from app.api.v1.health import router as health_router
from app.api.v1.upload import router as upload_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health_router, tags=["System and health"])
api_router.include_router(upload_router, tags=["File Management"])
