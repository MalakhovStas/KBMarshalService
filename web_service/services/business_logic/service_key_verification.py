from datetime import datetime
from services.loader import requests_manager, logger


async def key_verification(service: str, key: str) -> bool:
    result = False
    limit = 0
    spent = 0

    try:
        if service == 'FNS':
            if not key:
                key = 'add9a7f31295113260ec9f9bf6b701b06bdf355b'  # ключ для тестов
            result = (await requests_manager(url=f'https://api-fns.ru/api/stat?key={key}')).get("response")
            limit = int(result.get('Методы')['innfl']['Лимит'].strip())
            spent = int(result.get('Методы')['innfl']['Истрачено'].strip())

        elif service == 'FSSP':
            if not key:
                key = 'f12e71a48666aaa2eeef529fa361f5f4c249be6b'  # ключ для тестов
            result = (await requests_manager(f'https://api.damia.ru/fssp/stat?key={key}')).get("response")
            limit = int(result.get('Методы')['ispsfl']['Лимит'].strip())
            spent = int(result.get('Методы')['ispsfl']['Истрачено'].strip())

        date_limit = datetime.strptime(result.get('ДатаОконч'), "%Y-%m-%d %H:%M:%S")
        available = limit - spent
        date_limit_str = date_limit.strftime("%d.%m.%Y %H:%M")
        logger.debug(
            f'{f"Ключ {service} действителен до: {date_limit_str}" if date_limit > datetime.now() else f"Ключ {service} не действителен"}, '
            f'{f"Доступно запросов: {available}" if available > 0 else ""}'
        )
        result = True if date_limit > datetime.now() and available > 0 else False
    except Exception as exc:
        logger.error(f'Ошибка проверки ключа сервиса {service} | {exc=}')
        result = False
    return result
