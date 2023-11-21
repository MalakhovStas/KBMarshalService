"""Модуль конфигурации логирования"""
from loguru import logger
from .config import TG_BOT_BASE_DIR


debug_format = ("{time:DD-MM-YYYY at HH:mm:ss} | {level} | file: {file} "
                "| func: {function} | line: {line} | message: {message}")

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

PATH_FILE_DEBUG_LOGS = TG_BOT_BASE_DIR.joinpath("logs/tg_bot_debug.log")
PATH_FILE_ERRORS_LOGS = TG_BOT_BASE_DIR.joinpath("logs/tg_bot_errors.log")
PATH_FILE_RequestsManager = TG_BOT_BASE_DIR.joinpath("logs/tg_bot_RequestsManager.log")

LOGGER_DEBUG = {
    "sink": PATH_FILE_DEBUG_LOGS,
    "level": "DEBUG",
    "format": debug_format,
    **logger_common_args
}

LOGGER_ERRORS = {
    "sink": PATH_FILE_ERRORS_LOGS,
    "level": "WARNING",
    "format": errors_format,
    **logger_common_args
}

LOGGER_RequestsManager = {
    "sink": PATH_FILE_RequestsManager,
    "level": "DEBUG",
    "format": debug_format,
    "filter": lambda msg: msg.get("message").startswith('RequestsManager'),
    **logger_common_args
}


logger.add(**LOGGER_ERRORS)
logger.add(**LOGGER_DEBUG)
