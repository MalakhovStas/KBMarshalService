from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from django.shortcuts import render


class ServiceFNSPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FNS/fns_service.j2"

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            return render(request, self.template_name)
        else:
            return HttpResponseForbidden()


class ServiceFSSPPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FSSP/fssp_service.j2"

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            return render(request, self.template_name)
        else:
            return HttpResponseForbidden()