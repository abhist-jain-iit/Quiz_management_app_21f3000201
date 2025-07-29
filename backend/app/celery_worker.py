from celery import Celery
from celery.schedules import crontab
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

def make_celery(app=None):
    """Create and configure Celery instance with Flask app context"""
    celery = Celery(
        'quiz_master',
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND,
        include=['app.tasks']  # Include tasks module
    )

    if app:
        # Update celery config with Flask app config
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

# Create celery instance without app context to avoid circular imports
celery = make_celery()

# Configure scheduled tasks
celery.conf.beat_schedule = {
    # Daily reminders at 8:48 PM IST every day
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=20, minute=48),  # 8:48 PM IST daily
    },

    # Monthly reports on 1st of every month at 9 AM IST
    'generate-monthly-reports': {
        'task': 'app.tasks.generate_monthly_reports',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),  # 1st of month at 9 AM IST
    },

    # Clean up old task results every week
    'cleanup-old-results': {
        'task': 'app.tasks.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Monday 2 AM IST
    },
}

# Additional Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',  # Indian Standard Time
    enable_utc=False,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)