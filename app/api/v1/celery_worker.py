from app.celery_app import app as celery_app
from app.services.tasks import add
from celery.result import AsyncResult
from fastapi import APIRouter

router = APIRouter()


@router.post("/run-add-task")
def run_add_task(x: int, y: int):
    result = add.delay(x, y)
    return {"message": "Task queued successfully", "celery_task_id": result.id}


@router.get("/status/{celery_task_id}")
def get_add_result(celery_task_id: str):
    result = AsyncResult(celery_task_id, app=celery_app)
    print(result)
    if result.ready():
        return {"status": "completed", "result": result.result}
    return {"status": "processing"}
