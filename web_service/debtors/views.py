import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from .models import Debtor


def get_fullname(search_query: str) -> tuple:
    surname, name, patronymic = None, None, None
    if search_query:
        search_query = search_query.split(' ', maxsplit=2)
        if 0 < len(search_query) <= 3 and all([word.isalpha() for word in search_query]):
            if len(search_query) == 3:
                surname, name, patronymic = search_query
            elif len(search_query) == 2:
                surname, name, patronymic = search_query[0], search_query[1], ''
            elif len(search_query) == 1:
                surname, name, patronymic = search_query[0], None, None
    surname = surname.lower().title() if isinstance(surname, str) else surname
    name = name.lower().title() if isinstance(name, str) else name
    patronymic = patronymic.lower().title() if isinstance(patronymic, str) else patronymic
    return surname, name, patronymic


def get_passport(search_query: str) -> int | bool:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 10:
        result = search_query
    return result


def get_inn(search_query: str) -> int | bool:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 12:
        result = search_query
    return result


class DebtorDetailPageView(TemplateView):
    """ Отображение детальной информации о должнике """
    template_name = "/debtors/debtor_detail.j2"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            debtor = None
            if search_query := request.GET.get('search_query'):
                search_query = search_query.strip().lower()
                surname, name, patronymic = get_fullname(search_query)
                if surname and name and patronymic:
                    debtor = Debtor.objects.filter(surname=surname, name=name, patronymic=patronymic).first()
                elif surname and name:
                    debtor = Debtor.objects.filter(surname=surname, name=name).first()
                elif surname:
                    debtor = Debtor.objects.filter(surname=surname).first()
                elif passport := get_passport(search_query):
                    debtor = Debtor.objects.filter(ser_num_pass=passport).first()
                elif inn := get_inn(search_query):
                    debtor = Debtor.objects.filter(inn=inn).first()
            return render(request, self.template_name, context={'debtor': debtor})
        else:
            return HttpResponseForbidden()
