from celery.result import AsyncResult
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from services.business_logic.file_verification import load_data_file
from web_service.celery import app
from web_service.settings import redis_cache
from services.utils import get_redis_key, get_service_name
from django.http import FileResponse
from services.loader import logger


class BaseServicesPageView(TemplateView):
    template_name = ""

    def get_success_url(self):
        pass

    def get(self, request: WSGIRequest, *args, **kwargs):
        if request.user.groups.filter(name__in=['users', 'admins']).exists() or request.user.is_superuser:
            filename, task_file_verification, task_start_service = None, None, None

            if file_verification_data := redis_cache.get(get_redis_key(request=request, task_name='FILE_VERIFICATION')):
                task_file_verification_id, data = file_verification_data.split(sep=':', maxsplit=1)
                filename, task_result = data.split(':data:>', maxsplit=1)
                task_file_verification = AsyncResult(id=task_file_verification_id)

            if start_service_data := redis_cache.get(get_redis_key(request=request, task_name=f'START_SERVICE')):
                task_start_service_id, filename = start_service_data.split(sep=':', maxsplit=1)
                task_start_service = AsyncResult(id=task_start_service_id)

            context = {
                'filename': filename,
                'task_file_verification': task_file_verification,
                'task_start_service': task_start_service
            }
            logger.warning(f'CONTEXT: {context}')
            return render(request, self.template_name, context=context)
        else:
            return HttpResponseForbidden()

    def post(self, request: WSGIRequest, *args, **kwargs):

        """Метод изменения данных пользователя."""
        service = get_service_name(request)
        filename, task_file_verification, task_start_service = None, None, None

        if command := request.POST.get('command'):
            command, task_name, data = command.split(sep=':', maxsplit=2)

            if command == 'STOP_TASK':
                if task_name == 'ALL':
                    redis_cache.delete(get_redis_key(request=request, task_name='FILE_VERIFICATION'))
                    redis_cache.delete(get_redis_key(request=request, task_name='START_SERVICE'))
                else:
                    app.control.revoke(task_id=data, terminate=True)
                    redis_cache.delete(get_redis_key(request=request, task_name=task_name))
                return redirect(self.get_success_url())

            elif command == 'START_SERVICE':
                # get_redis_key(request=request, task_name=task_name)
                if service == 'FNS':
                    task_name = 'FILE_VERIFICATION'

                    if file_verification_data := redis_cache.get(name=get_redis_key(request=request, task_name=task_name)):
                        task_file_verification_id, data = file_verification_data.split(sep=':', maxsplit=1)
                        filename, task_result = data.split(':data:>', maxsplit=1)
                        logger.warning(f'task_result FROM REDIS: {task_result}')
                        task_file_verification = AsyncResult(id=task_file_verification_id)
                        logger.warning(f'task_result FROM CELERY: {task_file_verification.result}')

                    from services.business_logic.fns_service import start_parsing

                    msg, task_start_service, filename = start_parsing(request, filename)

                    messages.add_message(request, messages.INFO, msg)

                    # redis_cache.delete(get_redis_key(request=request, task_name=task_name))
                else:
                    return redirect(self.get_success_url())

            elif command == 'DOWNLOAD_RESULT_FILE':
                return FileResponse(open(f'media/{data}', "rb"))

        else:
            msg, task_file_verification, filename = load_data_file(request)
            messages.add_message(request, messages.INFO, msg)

        context = {
            'filename': filename,
            'task_file_verification': task_file_verification,
            'task_start_service': task_start_service
        }
        return render(request, self.template_name, context=context)


class ServiceFNSPageView(BaseServicesPageView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FNS/fns_service.j2"

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('services:fns_service')


class ServiceFSSPPageView(BaseServicesPageView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/services/FSSP/fssp_service.j2"

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('services:fssp_service')
