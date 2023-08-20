from django.contrib import admin
from debtors.models import Debtor


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    """Регистрация модели Debtor в админке"""
    ordering = ('surname', 'name', 'patronymic')
