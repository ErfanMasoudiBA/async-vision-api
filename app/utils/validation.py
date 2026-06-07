from app.config.settings import Settings
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


def validate_image_file(file: UploadFile, file_suffix: str, cfg: Settings) -> None:

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
