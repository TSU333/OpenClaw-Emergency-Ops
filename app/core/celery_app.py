from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "openclaw_emergency_ops",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=("app.workers.tasks",),
)
celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.timezone,
    enable_utc=True,
    imports=("app.workers.tasks",),
)
