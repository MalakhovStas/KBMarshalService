from loguru import logger

from .global_storage_logic import ServicesGlobalStorage
from .requests_manager import RequestsManager
from django.conf import settings

debug_format = (
    "{time:DD-MM-YYYY at HH:mm:ss} | {level} | file: {file} | "
    "func: {function} | line: {line} | message: {message}"
)

errors_format = "{time:DD-MM-YYYY at HH:mm:ss} | {level} | {file} | {message}"

security_format = "{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}"

logger_common_args = {
    "diagnose": True,
    "backtrace": False,
    "rotation": "10 Mb",
    "retention": 1,
    "compression": "zip",
}

print_exchange_response = True

PATH_FILE_DEBUG_LOGS = f"{settings.BASE_DIR}/logs/debug.log"
PATH_FILE_ERRORS_LOGS = f"{settings.BASE_DIR}/logs/errors.log"
PATH_FILE_RequestsManager = f"{settings.BASE_DIR}/logs/RequestsManager.log"
PATH_FILE_ServicesGlobalStorage = f"{settings.BASE_DIR}/logs/ServicesGlobalStorage.log"

LOGGER_DEBUG = {
    "sink": PATH_FILE_DEBUG_LOGS,
    "level": "DEBUG",
    "format": debug_format,
    **logger_common_args}

LOGGER_ERRORS = {
    "sink": PATH_FILE_ERRORS_LOGS,
    "level": "WARNING",
    "format": errors_format,
    **logger_common_args}

LOGGER_RequestsManager = {
    "sink": PATH_FILE_RequestsManager,
    "level": "DEBUG",
    "format": debug_format,
    "filter": lambda msg: msg.get("message").startswith('RequestsManager'),
    **logger_common_args}

LOGGER_ServicesGlobalStorage = {
    "sink": PATH_FILE_ServicesGlobalStorage,
    "level": "DEBUG",
    "format": debug_format,
    "filter": lambda msg: msg.get("message").startswith('ServicesGlobalStorage'),
    **logger_common_args}


logger.add(**LOGGER_DEBUG)
logger.add(**LOGGER_ERRORS)
logger.add(**LOGGER_RequestsManager)
logger.add(**LOGGER_ServicesGlobalStorage)

services_storage = ServicesGlobalStorage(logger=logger)
requests_manager = RequestsManager(logger=logger)
