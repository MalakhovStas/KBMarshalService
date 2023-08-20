import os

from django.core.handlers.wsgi import WSGIRequest
from web_service.settings import redis_cache


def get_redis_key(request: WSGIRequest, task_name: str) -> str:
    """Формирует имя ключа в Redis"""
    return f'{request.path.replace(os.sep, "_")}_last_task_{task_name}_user-{request.user.pk}'


def get_service_name(request: WSGIRequest) -> str:
    """Выделяет название сервиса из url endpoint"""
    return request.path.replace(os.sep, '').replace('services', '').upper()
