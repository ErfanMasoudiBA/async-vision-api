from random import randrange

from redis import Redis

from app.celery_app import app
from app.config.settings import get_settings

settings = get_settings()
redis = Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
JOB_TTL_SECONDS = 60 * 60 * 24  # 24h


@app.task()
def add(x: int, y: int) -> dict:
    return x + y


@app.task(bind=True, max_retries=3)
def predict(self, x: int) -> bool:
    job_id = self.request.id
    job_key = f"jobs:{job_id}"
    count = self.request.retries
    retries_left = self.max_retries - count
    redis.hset(job_key, mapping={"retries_left": retries_left})
    redis.expire(job_key, JOB_TTL_SECONDS)

    try:
        if not x == randrange(5):
            raise ValueError("Numbers do not match!")

        return True
    except Exception as e:
        self.retry(exc=e, args=[x], countdown=1)
