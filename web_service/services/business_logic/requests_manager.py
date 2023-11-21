import asyncio
from typing import Iterable, Any, Optional, Union, Dict, List

import aiohttp

from django.conf import settings


class RequestsManager:
    """Единая точка для отправки внешних запросов из всех модулей приложения"""

    __instance = None
    sign = None
    content_type = {"Content-Type": settings.DEFAULT_CONTENT_TYPE}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.sign = cls.__name__ + ": "
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, logger):
        self.logger = logger

    async def __call__(
            self,
            url: Optional[str] = None,
            method: str = "get",
            headers: Optional[Dict] = None,
            data: Union[Dict, List, None] = None,
            step: int = 1,
    ) -> Union[Dict, List]:
        """Повторяет запрос/запросы, если нет ответа или исключение"""

        if headers:
            headers = {**self.content_type, **headers}
        else:
            headers = self.content_type

        result = await self.aio_request(
            url=url,
            headers=headers,
            method=method,
            data=data,
        )
        if not result or not isinstance(result, dict):
            step += 1
            if step < settings.MAX_REQUEST_RETRIES:
                result = await self.__call__(
                    url=url,
                    headers=headers,
                    method=method,
                    data=data,
                    step=step,
                )
        return result

    async def aio_request(self, url: str, method: str = "get", headers: Optional[Dict] = None,
                          data: Optional[Union[Dict, List]] = None, timeout: int = settings.REQUESTS_TIMEOUT) -> Union[Dict, List]:
        """Основной метод http запросов, повторяет запрос, если во время выполнения запроса произошло исключение"""
        step = 1
        result = {}
        if not headers:
            headers = self.content_type
        # self.logger.debug(self.sign + f"{step=} -> request to: {url=} | {method=} | {data} | {headers}")

        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            while step < settings.MAX_REQUEST_RETRIES + 1:
                try:
                    if method == "post":
                        async with session.post(url, json=data, timeout=timeout) as response:
                            result = await self.__get_result(response=response)
                    else:
                        async with session.get(url, timeout=timeout) as response:
                            result = await self.__get_result(response=response, data=data)
                except Exception as exc:
                    text = (f"TRY AGAIN" if step < 3 else "BRAKE requests return ERROR")
                    result = {'response': {'error': f'{exc.__class__.__name__} {exc}'}, 'url': url,  **data}
                    # self.logger.warning(self.sign + f"ERROR -> {step=} -> {text} | {result=}")
                    step += 1
                else:
                    # self.logger.debug(self.sign + f"SUCCEED -> {step=} | return={result}")
                    break
        return result

    async def __get_result(self, response: aiohttp.ClientResponse, data: Optional[Dict] = None) -> Union[Dict[str, Any], List]:
        """Возвращает данные ответа"""
        result = None
        content = {"response": (await response.content.read()).decode("utf-8")}
        if data:
            content.update(data)
        try:
            if response.content_type in ["text/html", "text/plain"]:
                result = {"response": await response.text()}
            else:
                result = await response.json()
            if result and data:
                result.update(data)
        except Exception as exc:
            # self.logger.error(self.sign + f'response.content_type: {response.content_type} | {exc=}')
            pass
        return result if result else content
