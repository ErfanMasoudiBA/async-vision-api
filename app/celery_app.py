from celery import Celery

from app.config.settings import get_settings

settings = get_settings()

app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.tasks"],
)

app.conf.task_track_started = True
