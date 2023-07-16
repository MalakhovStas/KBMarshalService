from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_service.settings")
app = Celery("web_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# celery -A web_service worker -l info
