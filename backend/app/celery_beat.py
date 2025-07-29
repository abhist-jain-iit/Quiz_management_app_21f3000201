from celery.schedules import crontab
from .celery_worker import celery

# Configure Celery Beat schedule for automatic tasks
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=20, minute=48),  # 8:48 PM IST daily
    },
    'generate-monthly-reports': {
        'task': 'app.tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9 AM IST
    },
    'cleanup-old-files': {
        'task': 'app.tasks.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM IST
    },
}

celery.conf.timezone = 'Asia/Kolkata'  # Indian Standard Time
celery.conf.enable_utc = False
