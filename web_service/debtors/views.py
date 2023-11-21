from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import TemplateView
from utils import utils
from .models import Debtor



class DebtorDetailPageView(TemplateView):
    """ Отображение детальной информации о должнике """
    template_name = "/debtors/debtor_detail.j2"

    def get(self, request: WSGIRequest, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            debtor = None
            if search_query := request.GET.get('search_query'):
                search_query = search_query.strip().lower()
                surname, name, patronymic = utils.get_fullname(search_query)
                if surname and name and patronymic:
                    debtor = Debtor.objects.filter(surname=surname, name=name, patronymic=patronymic).first()
                elif surname and name:
                    debtor = Debtor.objects.filter(surname=surname, name=name).first()
                elif surname:
                    debtor = Debtor.objects.filter(surname=surname).first()
                elif passport := utils.get_passport(search_query):
                    debtor = Debtor.objects.filter(ser_num_pass=passport).first()
                elif inn := utils.get_inn(search_query):
                    debtor = Debtor.objects.filter(inn=inn).first()
                elif id_credit := utils.get_id_credit(search_query):
                    debtor = Debtor.objects.filter(id_credit=id_credit).first()

            return render(request, self.template_name, context={'debtor': debtor})
        else:
            return HttpResponseForbidden()
