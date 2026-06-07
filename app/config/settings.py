from functools import lru_cache
from pathlib import Path

from PIL import Image
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UPLOAD_DIR: Path = Path("uploads")
    CHUNK_SIZE: int = 65536
    IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".ico"}
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    MAX_IMAGE_PIXELS: int = 200_000_000


@lru_cache
def get_settings() -> Settings:

    settings = Settings()
    settings.UPLOAD_DIR.mkdir(exist_ok=True)
    Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS
    return settings
