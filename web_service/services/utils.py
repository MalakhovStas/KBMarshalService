import os

from django.core.handlers.wsgi import WSGIRequest
from web_service.settings import redis_cache


def get_redis_key(task_name: str, request: WSGIRequest | None = None, service: str | None = None, user: int | None = None) -> str:
    """Формирует имя ключа в Redis"""
    if service and user:
        return f'_services_{service.lower()}__last_task_{task_name}_user-{user}'
    return f'{request.path.replace(os.sep, "_")}_last_task_{task_name}_user-{request.user.pk}'


def get_service_name(request: WSGIRequest) -> str:
    """Выделяет название сервиса из url endpoint"""
    return request.path.replace(os.sep, '').replace('services', '').upper()
