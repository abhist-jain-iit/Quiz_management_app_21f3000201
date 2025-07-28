from celery import Celery
import os

# Celery configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

def make_celery(app=None):
    # Create and configure Celery instance 
    celery = Celery('quiz_master', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

# Create celery instance without app context to avoid circular imports
celery = make_celery()