from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest


def get_redis_key(request: WSGIRequest | HttpRequest, key_type):
    if key_type == 'file_verification':
        return f'{request.path}_last_file_verification_task_user-{request.user.pk}'