from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "bug_bounty_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.modules.recon.tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "app.modules.recon.tasks.*": {"queue": "recon"},
} 