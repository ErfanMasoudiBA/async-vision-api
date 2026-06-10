from app.celery_app import app


@app.task
def add(x: int, y: int) -> dict:
    result = x + y
    return {"result": result}
