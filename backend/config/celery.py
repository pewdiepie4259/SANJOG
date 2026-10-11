import os
from celery import Celery

# Set default Django settings module for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('sanjog')

# Load task configuration from Django settings using 'CELERY' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task modules from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
