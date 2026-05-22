from celery import Celery
from celery.schedules import crontab
from backend.config import settings

# Create Celery app
celery_app = Celery(
    'edumind_workers',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['backend.workers.notification_worker']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'backend.workers.notification_worker.*': {'queue': 'notifications'},
    },
    
    # Result backend
    result_expires=3600,  # 1 hour
    
    # Worker
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Celery Beat Schedule (for periodic tasks)
celery_app.conf.beat_schedule = {
    # Check for due notifications every minute
    'process-scheduled-notifications': {
        'task': 'backend.workers.notification_worker.process_scheduled_notifications',
        'schedule': crontab(minute='*'),  # Every minute
    },
    
    # Check for missed sessions every hour
    'check-missed-sessions': {
        'task': 'backend.workers.notification_worker.check_missed_sessions',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Daily progress summary at 8 PM
    'send-daily-summary': {
        'task': 'backend.workers.notification_worker.send_daily_summary',
        'schedule': crontab(hour=20, minute=0),  # 8 PM daily
    },
}
