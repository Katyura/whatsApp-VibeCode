"""Celery configuration for whatsApp-VibeCode"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('whatsApp-VibeCode')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule (periodic tasks)
app.conf.beat_schedule = {
    'cleanup-expired-statuses': {
        'task': 'apps.status.tasks.cleanup_expired_statuses',
        'schedule': crontab(minute=0),  # Run hourly
    },
    'update-last-seen': {
        'task': 'apps.users.tasks.update_inactive_users',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
