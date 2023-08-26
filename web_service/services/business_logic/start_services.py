from celery.result import AsyncResult
from django.core.handlers.wsgi import WSGIRequest
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from services.tasks import start_service_fns, start_service_fssp
from services.utils import get_service_name, get_redis_key
from web_service.settings import redis_cache


def start_services(request: WSGIRequest, filename, task_file_verification):
    service = get_service_name(request)
    task = False

    if service == 'FNS':
        task: AsyncResult = start_service_fns.delay(
            task_file_verification_id=task_file_verification.task_id,
            filename=filename,
            language=translation.get_language()
        )

    elif service == "FSSP":
        task: AsyncResult = start_service_fssp.delay(
            task_file_verification_id=task_file_verification.task_id,
            filename=filename,
            language=translation.get_language()
        )

    if task:
        redis_cache.set(
            name=get_redis_key(request=request, task_name=f'START_SERVICE'),
            value=f'{task.task_id}:{filename}'
        )

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
    return msg, task, filename