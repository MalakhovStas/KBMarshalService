from django.views.generic import TemplateView


class ServiceFNSPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FNS/fns_service.j2"


class ServiceFSSPPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FSSP/fssp_service.j2"
