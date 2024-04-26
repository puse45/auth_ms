import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.timezone = "UTC+3"
