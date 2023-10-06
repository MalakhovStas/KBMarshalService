import os
from datetime import datetime
from typing import Optional, Tuple

from dateutil import parser
from dateutil.parser import ParserError
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


def date_identifier_and_converter(value) -> Tuple:
    """Если на входе объект datetime -> преобразует в строку формата '%d.%m.%Y'.
       Если строка -> пытается преобразовать её в объект datetime и после преобразует в строку формата '%d.%m.%Y',
       если преобразовать не получилось - возвращает пустую строку"""
    # date_formats = [
    #     '%d.%m.%Y', '%d-%m-%Y', '%d_%m_%Y', '%d %m %Y', '%d/%m/%Y',
    #     '%Y.%m.%d', '%Y-%m-%d', '%Y_%m_%d', '%Y %m %d', '%Y/%m/%d',
    #     '%d.%B.%Y', '%d-%B-%Y', '%d_%B_%Y', '%d %B %Y', '%d/%B/%Y'
    # ]
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
