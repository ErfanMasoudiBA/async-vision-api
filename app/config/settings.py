from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    UPLOAD_DIR: Path = Path("uploads")
    CHUNK_SIZE: int = 65536
    IMAGE_EXTENSIONS: set[str] = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
    }
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    MAX_IMAGE_PIXELS: int = 200_000_000

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
