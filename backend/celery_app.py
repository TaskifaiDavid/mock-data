from celery import Celery
from celery.schedules import crontab
from app.utils.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "bibbi_cleaner",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Celery configuration
celery_app.conf.update(
    # Timezone settings
    timezone="Europe/Stockholm",
    enable_utc=True,
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600  # 1 hour
)

if __name__ == "__main__":
    celery_app.start()