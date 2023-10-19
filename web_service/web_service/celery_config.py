from __future__ import absolute_import
import os
from celery import Celery
from web_service.settings import REDIS_URL, TIME_ZONE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_service.settings")  # модуль с настройками django
app = Celery("web_service")  # приложение celery
app.config_from_object("django.conf:settings", namespace="CELERY")  # переменные для CELERY начинаются с этого слова
app.autodiscover_tasks()  # автоматический поиск задач

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
# настройки делаются так
app.conf.result_backend = "django-db"
app.conf.broker_url = REDIS_URL
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
# или так
app.conf.update(
    cache_backend='default',
    accept_content=['application/json'],
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    broker_connection_retry_on_startup=True,
    timezone=TIME_ZONE,
)
#python manage.py migrate django_celery_results
# print('type:', type(app.conf), '\n')
# print(app.conf)
# celery -A web_service worker -l info

#  celery beat инструкция если будет нужен
#  https://www.youtube.com/watch?v=jac2LQN6aYs