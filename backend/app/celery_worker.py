from celery import Celery
from celery.schedules import crontab
import os

def make_celery(app=None):
    celery = Celery(
        'quiz_master',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=['app.tasks']
    )

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    # Configure timezone
    celery.conf.timezone = 'Asia/Kolkata'
    celery.conf.enable_utc = False

    return celery

celery = make_celery()

# Configure beat schedule
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=21, minute=50),
    },
    'generate-monthly-reports': {
        'task': 'app.tasks.generate_monthly_reports',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),
    },
    'cleanup-old-results': {
        'task': 'app.tasks.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),
    },
}

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=False,
    task_track_started=True,
    task_time_limit=1800,
    worker_prefetch_multiplier=1,
    beat_schedule_filename='celerybeat-schedule',
)