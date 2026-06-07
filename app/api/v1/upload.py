from pathlib import Path

from app.config.settings import Settings, get_settings
from app.utils.file_helpers import create_unique_filename, read_write_file
from app.utils.validation import validate_image_file
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), cfg: Settings = Depends(get_settings)
):

    if file.filename is None:
        raise HTTPException(status_code=400, detail="missing filename")

    file_suffix = Path(file.filename).suffix.lower()

    validate_image_file(file, file_suffix, cfg)

    unique_filename = create_unique_filename(file_suffix)

    await read_write_file(file, unique_filename, cfg)

    return {"filename": unique_filename}
