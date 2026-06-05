import os
from celery import Celery

def make_celery(app_name="hms_tasks"):
    redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    celery_instance = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url
    )
    
    # Configure beat schedule for background appointment reminders
    celery_instance.conf.beat_schedule = {
        'send-appointment-reminders-every-12-hours': {
            'task': 'services.reminders.send_appointment_reminders_task',
            'schedule': 43200.0, # 12 hours in seconds
        },
    }
    celery_instance.conf.timezone = 'UTC'
    
    return celery_instance

celery = make_celery()
