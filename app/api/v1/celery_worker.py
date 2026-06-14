import uuid
from datetime import datetime, timezone

from celery.result import AsyncResult
from fastapi import APIRouter
from redis.asyncio import Redis

from app.celery_app import app as celery_app
from app.config.settings import get_settings
from app.services.tasks import add, predict

settings = get_settings()
router = APIRouter()
redis = Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
JOB_TTL_SECONDS = 60 * 60 * 24  # 24h


@router.post("/run-add-task")
async def run_add_task(x: int, y: int):
    job_id = str(uuid.uuid4())

    job_key = f"jobs:{job_id}"

    submitted_at = datetime.now(timezone.utc).isoformat()

    await redis.hset(job_key, mapping={"submitted_at": submitted_at})
    await redis.expire(job_key, JOB_TTL_SECONDS)

    add.apply_async(args=[x, y], task_id=job_id)
    return {
        "message": "Task queued successfully",
        "celery_task_id": job_id,
        "submitted_at": submitted_at,
    }


@router.post("/run_predict_task")
async def run_predict_task(x: int):
    job_id = str(uuid.uuid4())

    job_key = f"jobs:{job_id}"

    submitted_at = datetime.now(timezone.utc).isoformat()

    await redis.hset(job_key, mapping={"submitted_at": submitted_at})
    await redis.expire(job_key, JOB_TTL_SECONDS)

    predict.apply_async(args=[x], task_id=job_id)
    return {
        "message": "Task queued successfully",
        "celery_task_id": job_id,
        "submitted_at": submitted_at,
    }


@router.get("/status/{celery_task_id}")
async def get_add_result(celery_task_id: str):

    job_key = f"jobs:{celery_task_id}"
    job_data = await redis.hgetall(job_key)
    if not job_data:
        return {"status": "NOT_FOUND", "message": "Job ID does not exist"}
    result = AsyncResult(celery_task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "PENDING", "submitted_at": job_data["submitted_at"]}
    if result.state == "FAILURE":
        return {
            "status": "FAILURE",
            "error": str(result.info),
            "submitted_at": job_data["submitted_at"],
            "retries_left": job_data["retries_left"],
        }
    if result.successful():
        return {
            "status": "SUCCESS",
            "result": result.result,
            "submitted_at": job_data["submitted_at"],
            "retries_left": job_data["retries_left"],
        }

    # for STARTED status
    return {"status": result.state.lower()}
