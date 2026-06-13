from celery.result import AsyncResult
from fastapi import APIRouter

from app.celery_app import app as celery_app
from app.services.tasks import add

router = APIRouter()


@router.post("/run-add-task")
def run_add_task(x: int, y: int):
    result = add.delay(x, y)
    print(result.id)
    print(result.status)
    print(result.state)
    print(result.ready())
    print(result.successful())
    return {"message": "Task queued successfully", "celery_task_id": result.id}


@router.get("/status/{celery_task_id}")
def get_add_result(celery_task_id: str):
    result = AsyncResult(celery_task_id, app=celery_app)
    # print(result)
    # print(result.id)
    # print(result.status)
    # print(result.state)
    # print(result.ready())
    # print(result.successful())
    # print(result.result)
    if result.state == "PENDING":
        return {"message": "pending"}
    if result.state == "FAILURE":
        return {"status": "failed", "error": str(result.info)}
    if result.successful():
        return {"status": "completed", "result": result.result}
    return {"status": result.state.lower()}
