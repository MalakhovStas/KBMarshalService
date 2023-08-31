from datetime import datetime
import json
import os.path
from types import FunctionType
from typing import Any

import openpyxl
from django.conf import settings
from services.models import Service
from debtors.models import Debtor
from django.utils.translation import gettext_lazy as _


class ServicesGlobalStorage:
    """Класс для управления данными в оперативной памяти приложения"""
    __instance = None
    __DEBUG = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.sign = cls.__name__ + ": "
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, logger):
        services = Service.objects.all()
        self.storage = {service.title: {} for service in services}
        self.logger = logger
        self.decorate_methods()

    def get_object(self, service, task_file_verification_id, passport) -> dict | str | Any:
        # print(self.storage)
        return self.storage[service][task_file_verification_id][passport]

    def get_field(self, service, task_file_verification_id, passport, field_name) -> str | None:
        # все поля SessionDebtorModel должны быть str
        result = None
        if debtor := self.storage[service][task_file_verification_id][passport]:
            if isinstance(debtor, str):
                debtor_dict = json.loads(debtor)
                result = debtor_dict[field_name]
            elif isinstance(debtor, dict):
                result = debtor.get(field_name)
            else:
                if hasattr(debtor, field_name):
                    result = getattr(debtor, field_name)
        return result

    def add(self, service, task_file_verification_id, passport, data) -> bool:
        try:
            self.storage[service][task_file_verification_id]
        except KeyError:
            self.__add_operation_storage(service, task_file_verification_id)

        self.storage[service][task_file_verification_id][passport] = data
        return True

    def __add_operation_storage(self, service, task_file_verification_id):
        self.storage[service][task_file_verification_id] = {}
        return True

    def delete(self, service, task_file_verification_id, passport) -> bool:
        del self.storage[service][task_file_verification_id][passport]
        return True

    def update(self, service, task_file_verification_id, passport, data: dict) -> bool:
        if debtor := self.storage[service][task_file_verification_id][passport]:
            if isinstance(debtor, str):
                debtor_dict = json.loads(debtor)
                debtor_dict.update(data)
                self.storage[service][task_file_verification_id][passport] = json.dumps(debtor_dict)
            elif isinstance(debtor, dict):
                debtor.update(data)
            else:
                for field_name, value in data.items():
                    if hasattr(debtor, field_name):
                        setattr(debtor, field_name, value)
                        # debtor.__dict__[key] = value
            return True

    def add_passports_for_requests(
            self, service: str, task_file_verification_id: str, passports_for_requests: list) -> bool:
        self.storage[service][task_file_verification_id]['passports_for_requests'] = passports_for_requests
        print(self.storage)
        return True

    def get_passports_for_requests(self, service: str, task_file_verification_id: str) -> list:
        return self.storage[service][task_file_verification_id]['passports_for_requests']

    def add_passports_with_bad_results(
            self, service: str, task_file_verification_id: str, passports_with_bad_results: list) -> bool:
        self.storage[service][task_file_verification_id]['passports_with_bad_results'] = passports_with_bad_results
        return True

    def get_passports_with_bad_results(self, service: str, task_file_verification_id: str) -> list:
        return self.storage[service][task_file_verification_id]['passports_with_bad_results']

    def clear_operation_storage(self, service, task_file_verification_id) -> bool:
        del self.storage[service][task_file_verification_id]
        return True

    def clear_service_storage(self, service) -> bool:
        self.storage[service] = {}
        return True

    def save_operation_results(self, service, task_file_verification_id, filename) -> tuple[int, int]:

        save_file = filename.split(':')[-1]

        bad_result_objects = []
        passports_with_bad_results = self.storage[service][task_file_verification_id]['passports_with_bad_results']
        for passport in passports_with_bad_results:
            bad_result_objects.append(self.storage[service][task_file_verification_id][passport])
            del self.storage[service][task_file_verification_id][passport]

        self.save_objects_to_file(
            result_objects=bad_result_objects,
            service=service,
            filename=f'BAD_RESULT:{save_file}'
        )

        del self.storage[service][task_file_verification_id]['passports_for_requests']
        del self.storage[service][task_file_verification_id]['passports_with_bad_results']
        good_result_objects = list(self.storage[service][task_file_verification_id].values())
        self.save_objects_to_file(
            result_objects=good_result_objects,
            service=service,
            filename=f'RESULT:{save_file}'
        )
        return len(bad_result_objects), self.save_objects_to_db(result_objects=good_result_objects)

    @staticmethod
    def save_objects_to_file(result_objects, service, filename):
        """Сохраняет данные в файл"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(('Фамилия, имя, отчество', 'Дата рождения', 'Серия и номер паспорта', 'Дата выдачи паспорта', 'Кем выдан паспорт', 'ИНН'))
        for it_object in result_objects:
            ws.append((f'{it_object.surname} {it_object.name} {it_object.patronymic}', it_object.date_birth,
                       it_object.ser_num_pass, it_object.date_issue_pass, it_object.name_org_pass, it_object.inn))

        if not os.path.isdir(f'{settings.MEDIA_ROOT}/{service}/RESULTS'):
            os.mkdir(f'{settings.MEDIA_ROOT}/{service}/RESULTS')

        wb.save(f'{settings.MEDIA_ROOT}/{service}/RESULTS/{service}:{filename}')

    @staticmethod
    def save_objects_to_db(result_objects):
        for_db_result_objects = [result_object.to_dict() for result_object in result_objects]
        for result_object in for_db_result_objects:
            result_object.pop('url')
            result_object['date_birth'] = datetime.strptime(result_object['date_birth'], '%d.%m.%Y')
            result_object['date_issue_pass'] = datetime.strptime(result_object['date_issue_pass'], '%d.%m.%Y')
        Debtor.objects.bulk_create([Debtor(**result_object) for result_object in for_db_result_objects])
        return len(for_db_result_objects)

    @staticmethod
    def exception_wrapper(method: FunctionType):
        """Декоратор для логирования"""

        def wrapper(self, *args, **kwargs):
            result = None
            try:
                result = method(self, *args, **kwargs)
                if self.__DEBUG:
                    self.logger.debug(self.sign + f'method: {method.__name__.upper()} > {args=} | {kwargs=} | {result=}')
            except Exception as exc:
                self.logger.error(self.sign + f'method: {method.__name__.upper()} > {args=} | {kwargs=} | {exc.__class__.__name__} - {exc}')
            return result

        return wrapper

    @classmethod
    def decorate_methods(cls) -> None:
        """Для установки декоратора всем пользовательским методам"""
        for attr_name in cls.__dict__:
            if not attr_name.startswith('__') and attr_name not in ['']:
                method = cls.__getattribute__(cls, attr_name)
                if type(method) is FunctionType:
                    setattr(cls, attr_name, cls.exception_wrapper(method))
