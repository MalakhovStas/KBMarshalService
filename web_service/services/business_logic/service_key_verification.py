import asyncio
import json
from datetime import datetime
from typing import Dict

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _

from services.models import Service
from services.utils import get_service_name
from .loader import requests_manager, logger


def get_url(service_title):
    service = Service.objects.get(title=service_title)
    return service.methods.get(title='check_key').generate_url(key=service.key)


def key_verification(request: WSGIRequest) -> Dict:
    service = get_service_name(request)
    limit = 0
    spent = 0

    try:
        result = (asyncio.run(requests_manager(url=get_url(service)))).get("response")
        if isinstance(result, str):
            result = json.loads(result)

        if service == 'FNS':
            limit = int(result.get('Методы')['innfl']['Лимит'].strip())
            spent = int(result.get('Методы')['innfl']['Истрачено'].strip())

        elif service == 'FSSP':
            limit = int(result.get('Методы')['ispsfl']['Лимит'].strip())
            spent = int(result.get('Методы')['ispsfl']['Истрачено'].strip())

        date_limit = datetime.strptime(result.get('ДатаОконч'), "%Y-%m-%d %H:%M:%S")
        available = limit - spent

        if date_limit > datetime.now():
            msg = _("Key") + f' {service} ' + _("valid until") + f': {date_limit.strftime("%d.%m.%Y %H:%M")} | ' + \
                  _("Available requests") + f': {available}'
        else:
            msg = _("Key") + f' {service} ' + _("not valid")

        # logger.debug(msg)

        result = {
            "service": service,
            "key_valid": True if date_limit > datetime.now() and available > 0 else False,
            "valid_until": date_limit,
            "available_req": available,
            "error": False
        }
    except Exception as exc:
        msg = _('Key verification error, service: ') + service
        # logger.error(f'{msg} | {exc=}')

        result = {"service": service, "key_valid": False, "valid_until": False, "available_req": 0, "error": True}
    messages.add_message(request=request, level=messages.INFO, message=msg)
    return result

