import time

from django.views.generic import TemplateView
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from services.busness_logic import load_data_file
from web_service.settings import redis_cache

from celery import current_task
from celery_progress.backend import ProgressRecorder
from celery_progress import tasks
from celery.result import AsyncResult


class ServiceFNSPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FNS/fns_service.j2"

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('services:fns_service')

    def get(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
        """Метод изменения данных пользователя."""
        msg, task = load_data_file(request)
        # messages.add_message(request, messages.WARNING, 'Загрузка файла, валидация данных...')

        messages.add_message(self.request, messages.INFO, msg)
        return render(
            request,
            self.template_name,
            {'task': task}
        )

        # return HttpResponseRedirect(self.get_success_url(), {'task_id': task.task_id})


class ServiceFSSPPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FSSP/fssp_service.j2"

    def get(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
        """Метод изменения данных пользователя."""
        msg, task = load_data_file(request)
        # messages.add_message(request, messages.WARNING, 'Загрузка файла, валидация данных...')

        messages.add_message(self.request, messages.INFO, msg)
        return render(
            request,
            self.template_name,
            {'task': task}
        )