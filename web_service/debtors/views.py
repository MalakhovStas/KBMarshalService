from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden


class DebtorDetailPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/debtors/debtor_detail.j2"

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            return render(request, self.template_name)
        else:
            return HttpResponseForbidden()
