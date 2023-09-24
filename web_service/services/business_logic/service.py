import asyncio
import json
import time

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
        self.service_dm_model = Service.objects.get(title=service)
        self.task_file_verification_id = task_file_verification_id
        self.storage_kwargs = {'service': service, 'task_file_verification_id': task_file_verification_id}
        self.result_file_name = "RESULT:" + filename.split(':')[-1]
        self.logger = logger

    # @staticmethod
    async def start_group_request(self, group_request):
        # FIXME утверждение не верно, разобраться
        # await asyncio.sleep(1)  # обязательно перед запросом чтобы можно было запускать из синхронного кода
        # ожидание чтобы при обработке в цикле пачка запросов отправлялась не чаще 1раза в 1сек
        logger.warning(self.sign + 'start group request')
        start = time.time()
        result = await asyncio.gather(*group_request)
        time_spent = time.time() - start
        logger.warning(self.sign + f'group request completed {time_spent=}')
        if time_spent < 1:
            await asyncio.sleep(1-time_spent)
        return result

    def __call__(self, progress):
        passports_with_bad_results = []
        passports = services_storage.get_passports_for_requests(**self.storage_kwargs)

        groups = [
            passports[num:num + self.service_dm_model.num_person_in_group_request]
            for num in range(0, len(passports), self.service_dm_model.num_person_in_group_request)
        ]
        num_total_requests = len(groups)

        for num_group, group in enumerate(groups, 1):

            progress.set_progress(
                current=num_group,
                total=num_total_requests,
                description=_("Request") + f' # {num_group} | ' + _("total") + f': {num_total_requests}'
            )

            group_request = [
                requests_manager.aio_request(
                    url=services_storage.get_field(**self.storage_kwargs, passport=passport, field_name='url'),
                    data={'passport': passport},
                    timeout=self.service_dm_model.timeout_for_requests
                ) for passport in group
            ]

            results = asyncio.run(self.start_group_request(group_request))

            for result in results:
                inn = None
                isp_prs = None
                count = 0
                next_page = False
                passport = result['passport']
                raw_response = result['response']
                response = raw_response if isinstance(raw_response, dict) else json.loads(raw_response)
                error = response.get('error')

                if self.service_dm_model.title == "FNS" and response.get('items'):
                    inn = response.get('items')[0].get('ИНН')

                elif self.service_dm_model.title == "FSSP":
                    isp_prs = response.get("result")
                    count = response.get("count", 0)
                    next_page = response.get("next_page", False)
                    if isp_prs is None and not error:
                        error = str(response)

                if self.__DEBUG:
                    msg = f'{inn=}' if self.service_dm_model.title == "FNS" else f'quantity isp_prs: {count} | {next_page=}'
                    self.logger.debug(
                        self.sign + f'response from service {self.service_dm_model.title}: {error=} | {passport=} | {msg}'
                    )

                if not error:
                    if self.service_dm_model.title == "FNS" and inn is not None:
                        data = {'inn': inn}
                    elif self.service_dm_model.title == "FSSP" and isp_prs is not None:
                        data = {'isp_prs': isp_prs}
                    else:
                        data = {'error': f'{self.service_dm_model.title} service data processing is not configured'}
                else:
                    data = {'error': error}
                    passports_with_bad_results.append(passport)
                services_storage.update(**self.storage_kwargs, passport=passport, data=data)

            # Сохраняем полученные данные в БД после каждого 10го группового запроса
            if num_group % 10 == 0:
                services_storage.operations_with_debtors_in_db(
                    service=self.service_dm_model.title, task_file_verification_id=self.task_file_verification_id)

        services_storage.add_passports_with_bad_results(
            **self.storage_kwargs, passports_with_bad_results=passports_with_bad_results
        )
        return True
