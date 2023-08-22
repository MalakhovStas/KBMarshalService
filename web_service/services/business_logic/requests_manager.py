import asyncio
from typing import Iterable, Any

import aiohttp

from web_service.settings import REQUESTS_TIMEOUT, DEFAULT_CONTENT_TYPE, MAX_REQUEST_RETRIES


class RequestsManager:
    """Единая точка для отправки внешних запросов из всех модулей приложения"""

    __instance = None
    sign = None
    content_type = {"Content-Type": DEFAULT_CONTENT_TYPE}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.sign = cls.__name__ + ": "
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, logger):
        self.logger = logger

    async def __call__(
            self,
            url: str,
            method: str = "get",
            headers: dict | None = None,
            data: dict | list | None = None,
            list_requests: list | None = None,
            step: int = 1,
    ) -> dict | list:
        """Повторяет запрос/запросы, если нет ответа или исключение"""

        if headers:
            headers = self.content_type | headers
        else:
            headers = self.content_type

        if list_requests:
            result = await self.aio_request_gather(
                list_requests=list_requests, headers=headers, method=method, data=data
            )
        else:
            result = await self.aio_request(
                url=url,
                headers=headers,
                method=method,
                data=data,
            )
        if not result or not isinstance(result, dict):
            step += 1
            if step < MAX_REQUEST_RETRIES:
                result = await self.__call__(
                    url=url,
                    headers=headers,
                    method=method,
                    data=data,
                    list_requests=list_requests,
                    step=step,
                )
        return result

    async def aio_request(self, url: str, headers: dict,
                          method: str = "get", data: dict | list | None = None) -> dict | list:
        """Основной метод http запросов, повторяет запрос, если во время выполнения запроса произошло исключение"""
        step = 1
        result = dict()

        self.logger.debug(self.sign + f"{step=} -> request to: {url=} | {method=} | {data} | {headers}")

        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            while step < MAX_REQUEST_RETRIES + 1:
                try:
                    if method == "post":
                        async with session.post(url, json=data, timeout=REQUESTS_TIMEOUT) as response:
                            result = await self.__get_result(response=response)
                    else:
                        async with session.get(url, timeout=REQUESTS_TIMEOUT) as response:
                            result = await self.__get_result(response=response)
                except Exception as exc:
                    text = (f"TRY AGAIN" if step < 3 else "BRAKE requests return EMPTY DICT")
                    self.logger.warning(self.sign + f"ERROR -> {step=} | {exc=} | -> {text}")
                    step += 1
                else:
                    self.logger.debug(self.sign + f"SUCCEED -> {step=} | return={result}")
                    break
        return result

    async def __get_result(self, response: aiohttp.ClientResponse) -> dict[str, Any] | list:
        """Возвращает данные ответа"""
        result = None
        content = {"response": (await response.content.read()).decode("utf-8")}
        try:
            if response.content_type in ["text/html", "text/plain"]:
                result = {"response": await response.text()}
            else:
                result = await response.json()
        except Exception as exc:
            self.logger.error(self.sign + f'response.content_type: {response.content_type} | {exc=}')
        return result if result else content

    async def aio_request_gather(self, list_requests: list,
                                 headers: dict, method: str = "get", data: dict | None = None) -> Iterable:
        """Для отправки нескольких одновременных запросов"""

        if method == "post":
            tasks_data = [
                self.aio_request(url=url, headers=headers, method=method, data=data)
                for url in list_requests
            ]
        else:
            tasks_data = [self.aio_request(url=url, headers=headers) for url in list_requests]
        results = await asyncio.gather(*tasks_data)
        await asyncio.sleep(0.1)
        return results
