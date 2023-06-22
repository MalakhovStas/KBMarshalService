from django.shortcuts import render
from django.views.generic import TemplateView


class DebtorDetailPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/debtors/debtor_detail.j2"
