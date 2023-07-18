from celery.result import AsyncResult
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from services.busness_logic import load_data_file
from web_service.celery import app
from web_service.settings import redis_cache


class BaseServicesPageView:
    template_name = ""

    def get_success_url(self):
        pass

    def get(self, request: WSGIRequest, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            task = None
            redis_key = f'{request.path}_last_task_user-{request.user.pk}'
            if task_id := redis_cache.get(redis_key):
                task = AsyncResult(id=task_id)
                if task.status in ['SUCCESS', 'FAILURE', 'ERROR']:
                    redis_cache.delete(redis_key)
            return render(request, self.template_name, {'task': task})
        else:
            return HttpResponseForbidden()

    def post(self, request: WSGIRequest, *args, **kwargs):
        """Метод изменения данных пользователя."""

        if command := request.POST.get('command'):
            command, task_id = command.split(':')
            if command == 'STOP_TASK':
                app.control.revoke(task_id=task_id, terminate=True)
                return redirect(self.get_success_url())
        else:
            msg, task = load_data_file(request)
            messages.add_message(request, messages.INFO, msg)
            return render(request, self.template_name, {'task': task})


class ServiceFNSPageView(TemplateView, BaseServicesPageView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FNS/fns_service.j2"

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('services:fns_service')


class ServiceFSSPPageView(TemplateView, BaseServicesPageView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FSSP/fssp_service.j2"

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('services:fssp_service')
