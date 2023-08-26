from django.contrib import admin
from services.models import Service, Method


# class ServiceMethodParamInline(admin.StackedInline):
#     """Добавление метода в админке модели Service"""
#     model = Param


class ServiceMethodInline(admin.TabularInline):
    """Добавление метода в админке модели Service"""
    model = Method
    # inlines = [ServiceMethodParamInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Регистрация модели Service в админке"""
    ordering = ('date_added',)
    inlines = [ServiceMethodInline]


# @admin.register(Method)
# class MethodAdmin(admin.ModelAdmin):
#     """Регистрация модели Service в админке"""
#     ordering = ('date_added',)
#     inlines = [Param]
