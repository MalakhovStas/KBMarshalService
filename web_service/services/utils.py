import os
from typing import Optional

from django.core.handlers.wsgi import WSGIRequest


def get_redis_key(task_name: str, request: Optional[WSGIRequest] = None,
                  service: Optional[str] = None, user: Optional[int] = None) -> str:
    """Формирует имя ключа в Redis"""
    if service and user:
        return f'_services_{service.lower()}_last:{task_name}_user:{user}'
    return f'{request.path.replace(os.sep, "_")}_last:{task_name}_user:{request.user.pk}'


def get_service_name(request: WSGIRequest) -> str:
    """Выделяет название сервиса из url endpoint"""
    return request.path.replace(os.sep, '').replace('services', '').upper()
