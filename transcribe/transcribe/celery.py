import os
from celery import Celery

# Set the default Django settings module for the celery.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transcribe.settings")

# Create an instance of celery class named transcribe.
app = Celery("transcribe")
# Load task modules from Djnago app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
