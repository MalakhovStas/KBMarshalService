import asyncio
import json

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from services.models import Service
from .loader import requests_manager, services_storage, logger


class ServiceClass:
    __DEBUG = settings.DEBUG

    def __new__(cls, *args, **kwargs):
        cls.sign = cls.__name__ + ": "
        return super().__new__(cls)

    def __init__(self, service: str, filename: str, task_file_verification_id: str):
        self.service = service
        self.logger = logger
        self.num_person_in_group_request = Service.objects.get(title=self.service).num_person_in_group_request
        self.result_file_name = "RESULT:" + filename.split(':')[-1]
        self.storage_kwargs = {'service': self.service, 'task_file_verification_id': task_file_verification_id}

    @staticmethod
    async def start_group_request(group_request):
        await asyncio.sleep(1)  # обязательно перед запросом чтобы можно было запускать из синхронного кода
        # ожидание чтобы при обработке в цикле пачка запросов отправлялась не чаще 1раза в 1сек
        return await asyncio.gather(*group_request)

    def __call__(self, progress):
        passports_with_bad_results = []
        passports = services_storage.get_passports_for_requests(**self.storage_kwargs)

        groups = [
            passports[num:num + self.num_person_in_group_request]
            for num in range(0, len(passports), self.num_person_in_group_request)
        ]
        total = len(groups)
        for num, group in enumerate(groups, 1):
            progress.set_progress(
                current=num,
                total=total,
                description=f'{_("Group request")} {num} {_("out off")} {total}'
            )

            group_request = [
                requests_manager.aio_request(
                    url=services_storage.get_field(**self.storage_kwargs, passport=passport, field_name='url'),
                    data={'passport': passport}
                ) for passport in group
            ]

            results = asyncio.run(self.start_group_request(group_request))

            for result in results:
                print(result)
                passport = result['passport']

                response = json.loads(result['response'])
                items = response.get('items')
                error = response.get('error')

                if self.__DEBUG:
                    self.logger.debug(
                        self.sign + f'response from service {self.service}: {error=} | {passport=} | {items=}'
                    )

                if not error and items:
                    services_storage.update(
                        **self.storage_kwargs, passport=passport, data={'inn': items[0].get('ИНН')}
                    )
                else:
                    passports_with_bad_results.append(passport)

        services_storage.add_passports_with_bad_results(
            **self.storage_kwargs, passports_with_bad_results=passports_with_bad_results
        )
        return True
