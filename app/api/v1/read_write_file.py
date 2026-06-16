import uuid
from datetime import datetime, timezone
from pathlib import Path

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from redis.asyncio import Redis

from app.celery_app import app as celery_app
from app.config.settings import Settings, get_settings
from app.services.tasks import process_image_task
from app.utils.file_helpers import create_unique_filename, read_write_file
from app.utils.validation import validate_image_file

router = APIRouter()

settings = get_settings()
redis = Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
JOB_TTL_SECONDS = 60 * 60 * 24


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), cfg: Settings = Depends(get_settings)
):

    if file.filename is None:
        raise HTTPException(status_code=415, detail="missing filename")

    file_suffix = Path(file.filename).suffix.lower()
    validate_image_file(file, file_suffix, cfg)
    unique_filename = create_unique_filename(file_suffix)

    await read_write_file(file, unique_filename, cfg)

    file_path = str(cfg.UPLOAD_DIR / unique_filename)

    job_id = str(uuid.uuid4())
    job_key = f"jobs:{job_id}"
    submitted_at = datetime.now(timezone.utc).isoformat()

    await redis.hset(job_key, mapping={"submitted_at": submitted_at})
    await redis.expire(job_key, JOB_TTL_SECONDS)

    process_image_task.apply_async(args=[file_path], task_id=job_id)

    return {
        "filename": unique_filename,
        "task_id": job_id,
        "submitted_at": submitted_at,
        "message": "Image uploaded and processing started.",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    job_key = f"jobs:{task_id}"

    job_data = await redis.hgetall(job_key)
    if not job_data:
        return {"status": "NOT_FOUND", "message": "Job ID does not exist or expired"}

    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "PENDING", "submitted_at": job_data.get("submitted_at")}

    if result.state == "FAILURE":
        return {
            "status": "FAILURE",
            "error": str(result.info),
            "submitted_at": job_data.get("submitted_at"),
        }

    if result.successful():
        return {
            "status": "SUCCESS",
            "result": result.result,
            "submitted_at": job_data.get("submitted_at"),
        }

    return {"status": result.state, "submitted_at": job_data.get("submitted_at")}
