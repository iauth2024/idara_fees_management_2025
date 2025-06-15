from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myworld.settings')

# Create an instance of the Celery application.
app = Celery('myworld')

# Load configuration from Django settings.
# The namespace='CELERY' means all Celery-related settings should be prefixed with 'CELERY_' in settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps.
# Celery will look for a `tasks.py` file in each app directory.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: Configure periodic tasks (if you're using Celery Beat).
app.conf.beat_schedule = {
    'monitor-master-orders-every-10-seconds': {
        'task': 'myapp.tasks.monitor_master_orders',  # Path to the task
        'schedule': 10.0,  # Run every 10 seconds
    },
    'send-performance-alerts-every-5-minutes': {
        'task': 'myapp.tasks.send_performance_alerts',  # Path to the new task
        'schedule': 60.0,  # Run every 1 minutes (300 seconds)
    },
}

# Optional: Set up error handling and retries.
app.conf.task_annotations = {
    '*': {
        'retry': True,
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.5,
        },
    },
}

# Optional: Logging configuration.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')