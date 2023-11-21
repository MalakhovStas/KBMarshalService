import os
from datetime import datetime
from typing import Optional, Tuple

from dateutil import parser
from dateutil.parser import ParserError
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings


def get_redis_key(task_name: str, request: Optional[WSGIRequest] = None,
                  service: Optional[str] = None, user: Optional[int] = None) -> str:
    """Формирует имя ключа в Redis"""
    if service and user:
        result = f'_services_{service.lower()}__last:{task_name}_user:{user}'
    else:
        result = f'{request.path.replace(os.sep, "_")}_last:{task_name}_user:{request.user.pk}'
    return result


def get_service_name(request: WSGIRequest) -> str:
    """Выделяет название сервиса из url endpoint"""
    return request.path.replace(os.sep, '').replace('services', '').upper()


def date_identifier_and_converter(value) -> Tuple:
    """Если на входе объект datetime -> преобразует в строку формата '%d.%m.%Y'.
       Если строка -> пытается преобразовать её в объект datetime и после преобразует в строку формата '%d.%m.%Y',
       если преобразовать не получилось - возвращает пустую строку"""
    if isinstance(value, datetime):
        datetime_object = value
    elif isinstance(value, str):
        try:
            datetime_object = parser.parse(value)
        except (ValueError, ParserError, OverflowError) as exc:
            # logger.warning(f'Error parse date string {exc}')
            datetime_object = None
    else:
        datetime_object = None

    if datetime_object:
        string_result = datetime.date(datetime_object).strftime('%d.%m.%Y')
    else:
        string_result = ''

    return string_result, datetime_object


def get_results_file_abspath(service: str, filename: str) -> str:
    """Возвращает абсолютный путь к файлу результатов по имени файла и сервиса"""
    return f'{settings.MEDIA_ROOT}/{service}/results/{filename}'
