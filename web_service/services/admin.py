from django.contrib import admin
from services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Регистрация модели Service в админке"""
    ordering = ('date_added',)
