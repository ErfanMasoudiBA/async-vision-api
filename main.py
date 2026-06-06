import uuid
from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
CHUNK_SIZE = 65536
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".ico"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@app.get("/")
def read_root():
    return {"message": "Vision API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


def create_unique_filename(file: UploadFile) -> str:
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    return unique_filename


async def read_write_file(file: UploadFile, unique_filename: str) -> None:
    target = UPLOAD_DIR / unique_filename
    async with aiofiles.open(target, mode="wb") as buffer:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            await buffer.write(chunk)


def validate_image_file(file: UploadFile) -> None:
    if file.filename is None:
        raise HTTPException(status_code=400, detail="missing filename")
    if file.size is None or file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large or size unknown")

    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=415, detail="The file must be in picture format."
        )
    try:
        with Image.open(file.file) as img:
            img.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=415, detail="The file is not a picture.")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    validate_image_file(file)
    unique_filename = create_unique_filename(file)
    await read_write_file(file, unique_filename)
    return {"filename": unique_filename}
