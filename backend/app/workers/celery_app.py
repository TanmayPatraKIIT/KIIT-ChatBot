"""
Celery application configuration for background tasks.
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.config import settings
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'kiit_chatbot',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks (Celery Beat configuration)
celery_app.conf.beat_schedule = {
    # Scrape all sources every 6 hours
    'scrape-all-sources': {
        'task': 'app.workers.tasks.scrape_all_sources',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    # Rebuild FAISS index weekly
    'rebuild-faiss-index': {
        'task': 'app.workers.tasks.rebuild_faiss_index',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
    },
    # Cleanup old versions monthly
    'cleanup-old-versions': {
        'task': 'app.workers.tasks.cleanup_old_versions',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),  # 1st of month at 3 AM
    },
    # Generate daily stats at midnight
    'generate-daily-stats': {
        'task': 'app.workers.tasks.generate_daily_stats',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}

logger.info("Celery app configured with scheduled tasks")
