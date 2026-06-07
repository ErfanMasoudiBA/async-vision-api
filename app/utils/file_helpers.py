import uuid

import aiofiles
from app.config.settings import Settings
from fastapi import UploadFile


def create_unique_filename(file_suffix: str) -> str:
    return f"{uuid.uuid4()}{file_suffix}"


async def read_write_file(
    file: UploadFile, unique_filename: str, cfg: Settings
) -> None:
    target = cfg.UPLOAD_DIR / unique_filename
    async with aiofiles.open(target, mode="wb") as buffer:
        while True:
            chunk = await file.read(cfg.CHUNK_SIZE)
            if not chunk:
                break
            await buffer.write(chunk)
