from django.utils import translation
from django.core.handlers.wsgi import WSGIRequest

from services.utils import get_service_name, get_redis_key
from web_service.settings import redis_cache
from celery.result import AsyncResult
from services.tasks import start_service_fns
from django.utils.translation import gettext_lazy as _

from services.business_logic.service_key_verification import key_verification
import asyncio


def start_service(request: WSGIRequest, filename, task_file_verification):
    service = get_service_name(request)
    task: AsyncResult = start_service_fns.delay(language=translation.get_language())

    redis_cache.set(name=get_redis_key(request=request, task_name=f'START_SERVICE'), value=f'{task.task_id}:{filename}')

    # if request:
    #     filename = request
    #     task: AsyncResult = check_fields.delay(path=f'media/{filename}', language=translation.get_language())
    #     redis_cache.set(get_redis_key(request=request, task_name='file_verification'), f'{task.task_id}:{filename}')
    #     msg = _(f"File verification") + f": {file.name}"
    # else:
    #     msg = _('Unsupported file, .xls .xlsx only')
    # `else:
    #     msg = _("Select File")
    msg = f'{_("Start service")}: {service}'

    asyncio.run(key_verification(service=service, key=''))

    return msg, task, filename
