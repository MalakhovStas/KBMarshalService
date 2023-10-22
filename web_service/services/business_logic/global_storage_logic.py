from datetime import datetime
import json
import os.path
from types import FunctionType
from typing import Any, Union, Optional, Dict, List, Tuple

import openpyxl
from django.conf import settings
from django.db import transaction

from services.models import Service
from debtors.models import Debtor
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# from .session_models import SessionDebtorModel


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
        # services = ServiceTest.objects.all()
        # self.storage = {service.title: {} for service in services}
        # FIXME временная мера в связи с тем, что таблица создаётся позже чем экземпляр класса
        self.storage = {"FNS": {}, "FSSP": {}}
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        if not os.path.isdir(f'{settings.MEDIA_ROOT}/FNS'):
            os.mkdir(f'{settings.MEDIA_ROOT}/FNS')
        if not os.path.isdir(f'{settings.MEDIA_ROOT}/FSSP'):
            os.mkdir(f'{settings.MEDIA_ROOT}/FSSP')
        if not os.path.isdir(f'{settings.MEDIA_ROOT}/FNS/results'):
            os.mkdir(f'{settings.MEDIA_ROOT}/FNS/results')
        if not os.path.isdir(f'{settings.MEDIA_ROOT}/FSSP/results'):
            os.mkdir(f'{settings.MEDIA_ROOT}/FSSP/results')

        self.logger = logger
        self.decorate_methods()

    @staticmethod
    def exception_wrapper(method: FunctionType):
        """Декоратор для логирования"""
        def wrapper(self, *args, **kwargs):
            result = None
            try:
                result = method(self, *args, **kwargs)
                # if self.__DEBUG:
                #     self.logger.debug(self.sign + f'method: {method.__name__.upper()} > {args=} | {kwargs=} | {result=}')
            except Exception as exc:
                pass
                # self.logger.error(self.sign + f'method: {method.__name__.upper()} > {args=} | {kwargs=} | {exc.__class__.__name__} - {exc}')
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

    def get_task_object(self, service, task_file_verification_id, passport):
        """Возвращает объект SessionDebtorModel в случае исключения декоратор exception_wrapper вернёт None"""
        task_object = self.storage[service][task_file_verification_id][passport]
        return task_object if task_object.__class__.__name__ == 'SessionDebtorModel' else None

    def get_task_objects_list(self, service, task_file_verification_id) -> List:
        """Возвращает список объектов SessionDebtorModel из хранилища таски"""
        task_objects = []
        for session_debtor in self.storage[service][task_file_verification_id].values():
            if session_debtor.__class__.__name__ == 'SessionDebtorModel':
                task_objects.append(session_debtor)
        return task_objects

    def get_field(self, service, task_file_verification_id, passport, field_name) -> Optional[str]:
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

    def update(self, service, task_file_verification_id, passport, data: Dict) -> bool:
        """Обновляет значения полей SessionDebtor[passport] по данным data"""
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
            self, service: str, task_file_verification_id: str, passports_for_requests: List) -> bool:
        self.storage[service][task_file_verification_id]['passports_for_requests'] = passports_for_requests
        return True

    def get_passports_for_requests(self, service: str, task_file_verification_id: str) -> List:
        return self.storage[service][task_file_verification_id]['passports_for_requests']

    def add_passports_with_bad_results(
            self, service: str, task_file_verification_id: str, passports_with_bad_results: List) -> bool:
        self.storage[service][task_file_verification_id]['passports_with_bad_results'] = passports_with_bad_results
        return True

    def get_passports_with_bad_results(self, service: str, task_file_verification_id: str) -> List:
        return self.storage[service][task_file_verification_id]['passports_with_bad_results']

    def clear_operation_storage(self, service, task_file_verification_id) -> bool:
        """Удаляет словарь с данными таски"""
        del self.storage[service][task_file_verification_id]
        return True

    def clear_service_storage(self, service) -> bool:
        self.storage[service] = {}
        return True

    def save_operation_results(self, service: str, task_file_verification_id: str, filename: str) -> Tuple[int, int, int]:
        # self.logger.info(self.sign + f'УДАЛИТЬ!!! > storage: {self.storage}')
        incoming_file = filename.split(':')[-1]

        service_and_requests_errors = []
        passports_with_bad_results = self.storage[service][task_file_verification_id]['passports_with_bad_results']
        for passport in passports_with_bad_results:
            service_and_requests_errors.append(self.storage[service][task_file_verification_id][passport])
            del self.storage[service][task_file_verification_id][passport]

        if service_and_requests_errors:
            self.save_objects_to_file(
                result_objects=service_and_requests_errors,
                service=service,
                filename=f'{service}:service_and_requests_errors:{incoming_file}',
                bad_results=True,
            )

        del self.storage[service][task_file_verification_id]['passports_for_requests']
        del self.storage[service][task_file_verification_id]['passports_with_bad_results']

        debtors_for_save, debtors_for_update, add_debtors_to_result_file = self.selecting_objects_for_db_operations(
            service=service, task_file_verification_id=task_file_verification_id)

        self.save_objects_to_db(
            service=service, debtors_for_save=debtors_for_save, debtors_for_update=debtors_for_update)

        self.save_objects_to_file(
            result_objects=[*debtors_for_save, *debtors_for_update, *add_debtors_to_result_file],
            service=service,
            filename=f'{service}:result:{incoming_file}'
        )
        self.clear_operation_storage(service=service, task_file_verification_id=task_file_verification_id)
        return (len(service_and_requests_errors),
                len([*debtors_for_save, *debtors_for_update, *add_debtors_to_result_file]), len(debtors_for_save))

    @staticmethod
    def save_objects_to_file(result_objects: List, service: str, filename: str, bad_results: bool = False) -> None:
        """Сохраняет данные в файл"""
        wb = openpyxl.Workbook()
        ws = wb.active
        if service == "FNS":
            ws.append(('Id кредит', 'Фамилия, имя, отчество', 'Дата рождения', 'Серия и номер паспорта',
                       'Дата выдачи паспорта', 'Кем выдан паспорт', 'ОШИБКИ' if bad_results else 'ИНН'))
            for it_object in result_objects:
                ws.append((
                    it_object.id_credit,
                    f'{it_object.surname} {it_object.name} {it_object.patronymic  if it_object.patronymic else ""}',
                    it_object.date_birth,
                    it_object.ser_num_pass,
                    it_object.date_issue_pass,
                    it_object.name_org_pass if it_object.name_org_pass else "",
                    it_object.error if bad_results else it_object.inn if it_object.inn else ""
                ))

        elif service == "FSSP":
            ws.append(('Id кредит', 'Фамилия, имя, отчество', 'Дата рождения', 'Серия и номер паспорта',
                       'Дата выдачи паспорта', 'Кем выдан паспорт', 'ИНН',
                       'ОШИБКИ' if bad_results else 'Исполнительные производства'))
            for it_object in result_objects:
                if bad_results:
                    isp_prs_list = [it_object.error]
                else:
                    try:
                        isp_prs_list = [
                            key + '\n' + '\n'.join([f"{k}: {v}" for k, v in value.items() if v and k != "Должник"])
                            for key, value in it_object.isp_prs.items()] \
                            if isinstance(it_object.isp_prs, Dict) else ['Не найдено']
                    except Exception as exc:
                        isp_prs_list = [exc.__class__.__name__]

                ws.append((
                    it_object.id_credit,
                    f'{it_object.surname} {it_object.name} {it_object.patronymic  if it_object.patronymic else ""}',
                    it_object.date_birth,
                    it_object.ser_num_pass,
                    it_object.date_issue_pass,
                    it_object.name_org_pass if it_object.name_org_pass else "",
                    it_object.inn if it_object.inn else "",
                    *isp_prs_list
                ))
        else:
            ws.append((f'Настройки сохранения данных, результатов работы сервиса:{service} не найдены. '
                       f'Для обновления/добавления логики обратитесь к разработчику: {settings.DEVELOPER}',))
        wb.save(f'{settings.MEDIA_ROOT}/{service}/results/{filename}')

    def operations_with_debtors_in_db(self, service: str, task_file_verification_id: str,
                                      passports_mid_save: Optional[list] = None) -> bool:
        """Для вызова сохранения/обновления данных должников в БД, на основе имеющихся данных в global_storage.
        Из любой точки приложения в любой момент времени."""
        debtors_for_save, debtors_for_update, add_debtors_to_result_file = self.selecting_objects_for_db_operations(
            service=service,
            task_file_verification_id=task_file_verification_id,
            passports_mid_save=passports_mid_save
        )

        return self.save_objects_to_db(
            service=service,
            debtors_for_save=debtors_for_save,
            debtors_for_update=debtors_for_update
        )

    def selecting_objects_for_db_operations(self, service: str, task_file_verification_id: str,
                                            passports_mid_save: Optional[list] = None) -> Tuple[List, List, List]:
        """Выбор объектов SessionDebtorModel для совершения операций(сохранения/обновления) должников в БД"""
        debtors_for_save = []
        debtors_for_update = []
        add_debtors_to_result_file = []

        if passports_mid_save:
            selecting_list = [self.get_task_object(
                service, task_file_verification_id, passport) for passport in passports_mid_save]
        else:
            selecting_list = self.get_task_objects_list(service, task_file_verification_id)

        for session_debtor in selecting_list:
            if session_debtor:
                if not session_debtor.debtor_in_db:
                    debtors_for_save.append(session_debtor)
                else:
                    if service == "FNS" and session_debtor.inn:
                        if session_debtor.update_in_db and not session_debtor.all_db_operations_completed:
                            debtors_for_update.append(session_debtor)
                        else:
                            add_debtors_to_result_file.append(session_debtor)
                    elif service == "FSSP" and session_debtor.isp_prs is not None:
                        if session_debtor.update_in_db and not session_debtor.all_db_operations_completed:
                            debtors_for_update.append(session_debtor)
                        else:
                            add_debtors_to_result_file.append(session_debtor)
                    # не уверен, что это правильное решение
                    if (session_debtor.update_in_db and not session_debtor.all_db_operations_completed
                            and session_debtor not in debtors_for_update):
                        debtors_for_update.append(session_debtor)
        return debtors_for_save, debtors_for_update, add_debtors_to_result_file

    @staticmethod
    def save_objects_to_db(service: str, debtors_for_save: List, debtors_for_update: List) -> bool:
        """Сохраняет в БД объекты SessionDebtor из global_storage.storage[task_id] в которых debtor_in_db == False и
           обновляет объекты в которых debtor_in_db == True и update_in_db=True из списка debtors_for_update"""

        if debtors_for_save:
            if service == 'FNS':
                update_fields = ['inn']
            elif service == 'FSSP':
                update_fields = ['isp_prs']
            else:
                update_fields = ['name']  # нужно что-то указать

            debtors_for_save_elements_as_dict = [session_debtor.to_dict() for session_debtor in debtors_for_save]
            for session_debtor_dict in debtors_for_save_elements_as_dict:
                session_debtor_dict.pop('url')
                session_debtor_dict['date_birth'] = datetime.strptime(
                    session_debtor_dict['date_birth'], '%d.%m.%Y') if session_debtor_dict['date_birth'] else None
                session_debtor_dict['date_issue_pass'] = datetime.strptime(
                    session_debtor_dict['date_issue_pass'], '%d.%m.%Y') \
                    if session_debtor_dict['date_issue_pass'] else None

            Debtor.objects.bulk_create(
                [Debtor(**session_debtor) for session_debtor in debtors_for_save_elements_as_dict],
                update_conflicts=True, unique_fields=['ser_num_pass'], update_fields=update_fields)

        if debtors_for_update:
            with transaction.atomic():
                #  Согласно - https://www.sankalpjonna.com/learn-django/running-a-bulk-update-with-django
                #  эта операция эффективнее чем bulk_update
                for session_debtor in debtors_for_update:
                    update_fields = {}

                    if session_debtor.id_credit:
                        # обновляет id кредит в БД
                        # (попадёт сюда только если в БД не было этого поля или оно отличалось от данных в файле)
                        update_fields.update({'id_credit': session_debtor.id_credit})

                    if service == "FNS" and session_debtor.inn:
                        # обновляет ИНН в БД
                        update_fields.update({'inn': session_debtor.inn})

                    elif service == "FSSP" and session_debtor.isp_prs:
                        # обновляет исп. производства в БД
                        update_fields.update({'isp_prs': session_debtor.isp_prs})

                    Debtor.objects.filter(ser_num_pass=session_debtor.ser_num_pass).update(**update_fields)

        # Отмечаем в SessionDebtorModel, что все операции с БД для этого должника завершены и он в находится в БД
        for session_debtor in [*debtors_for_save, *debtors_for_update]:
            session_debtor.debtor_in_db = True
            session_debtor.all_db_operations_completed = True

        return True
