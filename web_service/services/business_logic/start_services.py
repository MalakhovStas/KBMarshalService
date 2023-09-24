from typing import Optional, Tuple

from celery.result import AsyncResult
from django.core.handlers.wsgi import WSGIRequest
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from services.tasks import start_fns_fssp_service
from services.utils import get_service_name, get_redis_key
from web_service.settings import redis_cache


def start_services(request: WSGIRequest, filename: str, task_file_verification: AsyncResult,
                   available_requests: int) -> Tuple[str, Optional[AsyncResult]]:
    """Запускает celery.task - старт сервисов"""
    service = get_service_name(request)
    task = None

    if service in ['FNS', 'FSSP']:
        task: AsyncResult = start_fns_fssp_service.delay(
            service=service,
            task_file_verification_id=task_file_verification.task_id,
            filename=filename,
            available_requests=available_requests,
            language=translation.get_language()
        )

    if task:
        redis_cache.set(
            name=get_redis_key(request=request, task_name=f'START_SERVICE'),
            value=f'{task.task_id}:{filename}'
        )

    msg = f'{_("Start service")}: {service}'
    return msg, task
