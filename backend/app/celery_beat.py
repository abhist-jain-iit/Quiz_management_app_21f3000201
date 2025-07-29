from celery.schedules import crontab
from .celery_worker import celery

# Configure Celery Beat schedule for automatic tasks
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # Daily at 6 PM
    },
    'generate-monthly-reports': {
        'task': 'app.tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of every month at 9 AM
    },
    'cleanup-old-files': {
        'task': 'app.tasks.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

celery.conf.timezone = 'UTC'
