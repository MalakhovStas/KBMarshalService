"""
Django settings for web_service project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

import django.conf
import redis
from dotenv import dotenv_values
from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _
import os

config = dotenv_values(os.path.join("..", ".env"))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%r@6@4js*-&ie)y+kd03cqr^b4^5bpy+()^!53qo*sf3#i8qtx'

# Данные о компании
COMPANY_PHONES = [
    (_('Collection department'), '+7-495-513-11-46'),  # Отдел взыскания
    (_('Contact department'), '+7-931-521-13-46'),  # Отдел обращений
    (_('Legal service'), '+7-495-927-58-32'),  # Юридическая служба
]
COMPANY_EMAIL = ('E-mail', 'kbmarshal@mail.ru')
COMPANY_ADDRESS = (_('Address'), _('Moscow, st.Narodnogo Opolcheniya.34, build.1, room.1/1'))
COMPANY_WORKING_HOURS = (_('Working time'), _('weekdays from 10:00 to 19:00'))

# Вспомогательные тексты
LOGIC_IN_DEV = _('Functionality of this block is under development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # "django.contrib.sites",
    # "django_extensions",
    'django_celery_results',
    'celery_progress',
    'corsheaders',
    'django_jinja',
    'phonenumber_field',
    'users',
    'account',
    'debtors',
    'services',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_service.urls'

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")


TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [Path(BASE_DIR).joinpath("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            # django-jinja defaults
            "match_extension": ".j2",
            "match_regex": None,
            "app_dirname": "templates",

            # Can be set to "jinja2.Undefined" or any other subclass.
            "undefined": None,
            "newstyle_gettext": True,
            "tests": {
                # "mytest": "path.to.my.test",
            },
            "filters": {
                'myi18n': django
                # "myfilter": "path.to.my.filter",
            },
            "globals": {
                # "myglobal": "path.to.my.globalfunc",
            },
            "constants": {
                'company_phones': COMPANY_PHONES,
                'company_email': COMPANY_EMAIL,
                'company_address': COMPANY_ADDRESS,
                'company_working_hours': COMPANY_WORKING_HOURS,
                'logic_in_dev': LOGIC_IN_DEV,
                # 'settings': django.conf.settings
                # "foo": "bar",
            },
            "policies": {
                "ext.i18n.trimmed": True,
            },

            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.DebugExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "django_jinja.builtins.extensions.DjangoExtraFiltersExtension",
            ],

            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },

            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",

            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],

        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],

        },
    },
]


WSGI_APPLICATION = 'web_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database/db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.ndjagoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = 'static/'
STATIC_URL = "/static/"
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = [
    "127.0.0.1"
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

FIXTURE_DIRS = [
    BASE_DIR / 'fixtures',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Данные для отправки сообщений на почту пользователя.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# FIXME - ValueError: Unable to configure handler 'file'
#  такая ошибка из-за логирования, позже разобраться
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#             'console': {'format': '%(asctime)s %(name)-12s %(levelname)-6s %(message)s'},
#             'file': {'format': '%(asctime)s %(name)-12s %(levelname)-6s %(message)s'}
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'console'
#         },
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'formatter': 'file',
#             'filename': 'debug.log'
#         }
#     },
#     'root': {
#         'handlers': ['console', 'file'],
#         'level': 'DEBUG',
#         'propagate': True
#     }
# }

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'unsafe-none'
CORS_ALLOW_ALL_ORIGINS = True  # Добавляет заголовок "Access-Control-Allow-Headers: * "
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['OPTIONS', 'GET', 'POST']
CORS_ALLOW_HEADERS = list(default_headers) + [
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Credentials",
    "accept",
    "accept-encoding",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "X-Amz-Date"
]

# Переопределение переменных в local_settings
from web_service.local_settings import *

from redis import StrictRedis

REDIS_URL = f"redis://{config['REDIS_HOST']}:{config['REDIS_PORT']}/{config['REDIS_DATABASE']}"
redis_cache = StrictRedis(
    host=config['REDIS_HOST'],
    port=int(config['REDIS_PORT']),
    db=int(config['REDIS_DATABASE']),
    decode_responses=True,
    charset="utf-8",
)

# CELERY
CELERY_BROKER_URL = REDIS_URL  # для rabbitmq, поменяйте адрес брокера на amqp://guest:guest@127.0.0.1:5672
CELERY_TASK_TRACK_STARTED = True  # запускает трекинг задач Celery

# # Планировщик задач
#
# # Celery настроен на использование планировщика из базы данных
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
#
# CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}  # время ожидания видимости 1 час
CELERY_ACCEPT_CONTENT = ['application/json']  # это тип содержимого, разрешенный к получению
CELERY_TASK_SERIALIZER = 'json'  # это строка, используемая для определения метода сериализации по умолчанию
CELERY_RESULT_BACKEND = 'django-db'  # указание для django_celery_results куда записывать результат выполнения задач

# это не из видео а интуитивно
CELERY_RESULT_SERIALIZER = 'json'  # является типом формата сериализации результатов
CELERY_TASK_DEFAULT_QUEUE = 'default-queue'  # celery будет использовать это имя очереди

# с тем что ниже пока не разобрался
#
# CART_SESSION_ID = 'cart'
# DELIVERY_SESSION_ID = 'delivery_id'
#
# # Always use IPython for shell_plus
# SHELL_PLUS = "ipython"
# SHELL_PLUS_PRINT_SQL = True
#
# # To disable truncation of sql queries use
# SHELL_PLUS_PRINT_SQL_TRUNCATE = None
#
# # Specify sqlparse configuration options when printing sql queries to the console
# SHELL_PLUS_SQLPARSE_FORMAT_KWARGS = dict(
#     reindent_aligned=True,
#     truncate_strings=500,
# )
#
# # Specify Pygments formatter and configuration options when printing sql queries to the console
# SHELL_PLUS_PYGMENTS_FORMATTER = pygments.formatters.TerminalFormatter
# SHELL_PLUS_PYGMENTS_FORMATTER_KWARGS = {}
#
# LOGIN_URL = reverse_lazy('users:login_user')

#
# # Данные почты получателя уведомлений о проведённом импорте
# RECIPIENTS_EMAIL = ['service.megano@gmail.com']   # список получателей по умолчанию
# DEFAULT_FROM_EMAIL = 'service.megano@gmail.com'  # почта администратора
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'