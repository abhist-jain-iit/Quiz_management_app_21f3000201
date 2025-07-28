#!/usr/bin/env python3
"""
Celery worker entry point for Quiz Master application.
Run this file to start the Celery worker process.

Usage:
    python celery_worker.py worker --loglevel=info
    python celery_worker.py beat --loglevel=info
"""

import os
import sys
from app import create_app
from app.celery_worker import make_celery

def create_celery_app():
    """Create Flask app and configure Celery"""
    flask_app = create_app()
    celery = make_celery(flask_app)
    return celery, flask_app

if __name__ == '__main__':
    celery_app, flask_app = create_celery_app()
    
    # Import tasks to register them
    from app.tasks import *
    
    # Configure Celery beat schedule
    celery_app.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'app.tasks.send_daily_reminders',
            'schedule': 86400.0,  # Run every 24 hours (86400 seconds)
            # 'schedule': crontab(hour=18, minute=0),  # Run daily at 6 PM
        },
        'send-monthly-reports': {
            'task': 'app.tasks.send_monthly_reports',
            'schedule': 2592000.0,  # Run every 30 days (2592000 seconds)
            # 'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Run on 1st of every month at 9 AM
        },
    }
    
    celery_app.conf.timezone = 'UTC'
    
    # Start Celery worker or beat scheduler based on command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'worker':
            # Start worker
            celery_app.worker_main(['worker', '--loglevel=info'])
        elif sys.argv[1] == 'beat':
            # Start beat scheduler
            celery_app.start(['beat', '--loglevel=info'])
        else:
            print("Usage: python celery_worker.py [worker|beat]")
            print("  worker - Start Celery worker")
            print("  beat   - Start Celery beat scheduler")
    else:
        print("Usage: python celery_worker.py [worker|beat]")
        print("  worker - Start Celery worker")
        print("  beat   - Start Celery beat scheduler")
