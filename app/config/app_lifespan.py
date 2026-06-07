from contextlib import asynccontextmanager

from app.config.settings import get_settings
from fastapi import FastAPI
from PIL import Image


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    settings = get_settings()
    settings.UPLOAD_DIR.mkdir(exist_ok=True)
    Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS

    yield
