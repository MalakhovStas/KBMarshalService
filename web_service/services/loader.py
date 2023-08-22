from loguru import logger
# from redis import StrictRedis
from services.business_logic.requests_manager import RequestsManager


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

PATH_FILE_DEBUG_LOGS = "./logs/debug.log"
PATH_FILE_ERRORS_LOGS = "./logs/errors.log"
PATH_FILE_RequestsManager = "./logs/RequestsManager.log"

LOGGER_DEBUG = {
    "sink": PATH_FILE_DEBUG_LOGS,
    "level": "DEBUG",
    "format": debug_format,
} | logger_common_args

LOGGER_ERRORS = {
    "sink": PATH_FILE_ERRORS_LOGS,
    "level": "WARNING",
    "format": errors_format,
} | logger_common_args

LOGGER_RequestsManager = {
    "sink": PATH_FILE_RequestsManager,
    "level": "DEBUG",
    "format": debug_format,
    "filter": lambda msg: msg.get("message").startswith('RequestsManager')
} | logger_common_args


logger.add(**LOGGER_DEBUG)
logger.add(**LOGGER_ERRORS)
logger.add(**LOGGER_RequestsManager)

# redis_cache = StrictRedis(
#     host=settings.REDIS_DATA.get("host"),
#     port=settings.REDIS_DATA.get("port"),
#     db=settings.REDIS_DATA.get("database"),
#     decode_responses=True,
#     charset="utf-8",
# )

# lock = redis_cache.lock("webhook-xt-logic", timeout=10)
# lock.acquire(blocking_timeout=10)


# async def create_instances_async_classes():
#     auth_instance = await XTLogicAuth(logger=logger, redis_cache=redis_cache)
#     return auth_instance

# loop = asyncio.get_event_loop()
# task = loop.create_task(create_instances_async_classes())
# auth = loop.run_until_complete(task)

requests_manager = RequestsManager(logger=logger)
