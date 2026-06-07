import uuid
from pathlib import Path

import aiofiles
from app.config.settings import Settings, settings
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Vision API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


def create_unique_filename(file_suffix: str) -> str:
    return f"{uuid.uuid4()}{file_suffix}"


def get_settings():
    return settings


async def read_write_file(
    file: UploadFile, unique_filename: str, cfg: Settings = Depends(get_settings)
) -> None:
    target = cfg.UPLOAD_DIR / unique_filename
    async with aiofiles.open(target, mode="wb") as buffer:
        while True:
            chunk = await file.read(cfg.CHUNK_SIZE)
            if not chunk:
                break
            await buffer.write(chunk)


def validate_image_file(
    file: UploadFile, file_suffix: str, cfg: Settings = Depends(get_settings)
) -> None:

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > cfg.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large")

    if file_suffix not in cfg.IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=415, detail="The file must be in picture format."
        )
    try:
        with Image.open(file.file) as img:
            img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=415, detail="The file is not a valid picture.")
    finally:
        file.file.seek(0)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="missing filename")

    file_suffix = Path(file.filename).suffix.lower()

    validate_image_file(file, file_suffix)

    unique_filename = create_unique_filename(file_suffix)

    await read_write_file(file, unique_filename)

    return {"filename": unique_filename}
