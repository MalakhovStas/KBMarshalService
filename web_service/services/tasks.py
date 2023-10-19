import os
from datetime import timedelta
from typing import Dict

import openpyxl
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from openpyxl.worksheet.worksheet import Worksheet

from debtors.models import Debtor
from services.business_logic.custom_progress import CustomProgressRecorder
from services.business_logic.exceptions import FileVerificationException
from services.business_logic.file_reader import FileReader
from services.business_logic.loader import services_storage
from services.business_logic.service import ServiceClass
from services.models import Service
# from loguru import logger


@shared_task(bind=True, name='check_file_fields')
def check_file_fields(self, service, filename, language=None) -> str:
    # logger.debug('start celery task - check_file_fields')
    # FIXME
    from .business_logic.file_verification import Checker

    path_to_file = f'{settings.MEDIA_ROOT}/{service}/{filename}'

    prev_language = translation.get_language()
    language and translation.activate(language)

    checker = Checker(service)

    sheet: Worksheet = openpyxl.load_workbook(path_to_file).active
    for num, (field, data) in enumerate(checker.fields_table.items(), 1):
        CustomProgressRecorder(self).set_progress(
            title=_('Checking if there is data in a file'),
            current=num,
            total=len(checker.fields_table.keys()),
            description=_('Searching') + f': {checker.trans_fields[field]}'
        )
        if not data['column'] and not data['row']:
            for title_row, column in checker.search_title_gen(max_column=sheet.max_column):
                if column not in checker.detected_columns:
                    if checker.check_field(field=field, title_row=title_row, column=column, sheet=sheet):
                        break

    # Должна быть такая последовательность для правильного перевода
    result = checker.check_fields_result(sheet)
    translation.activate(prev_language)
    # logger.debug(f'completed the celery task - check_file_fields, {result=}')
    return result


@shared_task(bind=True, name='start_fns_fssp_service')
def start_fns_fssp_service(self, service: str, filename: str,
                           task_file_verification_id: str, available_requests: int, language=None) -> Dict:
    # logger.debug('start celery task - start_fns_fssp_service')
    prev_language = translation.get_language()
    language and translation.activate(language)

    # logger.debug('start file_reader in task start_fns_fssp_service')
    file_reader = FileReader(service, task_file_verification_id, filename)
    unique_passports, incorrect_data_or_duplicates = file_reader(
        progress=CustomProgressRecorder(self, title=_('File data loading'))
    )

    persons_in_db = Debtor.objects.in_bulk(unique_passports, field_name='ser_num_pass')

    passports_for_request = []

    days_data_lifetime_from_service = Service.objects.get(title=service).days_data_lifetime_from_service

    for session_debtor in services_storage.storage[service][task_file_verification_id].values():
        if session_debtor.ser_num_pass in persons_in_db.keys():
            session_debtor.debtor_in_db = True
            debtor_from_db = persons_in_db[session_debtor.ser_num_pass]  # выбираем объект БД

            if not debtor_from_db.id_credit or debtor_from_db.id_credit != session_debtor.id_credit:
                session_debtor.update_in_db = True

            if service == "FNS":
                if not debtor_from_db.inn:
                    session_debtor.update_in_db = True
                    passports_for_request.append(session_debtor.ser_num_pass)
                else:
                    session_debtor.inn = debtor_from_db.inn
            elif service == "FSSP":
                if not session_debtor.inn and debtor_from_db.inn:
                    session_debtor.inn = debtor_from_db.inn
                session_debtor.isp_prs = debtor_from_db.isp_prs  # записываем isp_prs из БД в SessionDebtorModel
                if not debtor_from_db.isp_prs or (timezone.now() - debtor_from_db.modification_date
                                                  >= timedelta(days=days_data_lifetime_from_service)):
                    session_debtor.update_in_db = True
                    passports_for_request.append(session_debtor.ser_num_pass)

        else:
            passports_for_request.append(session_debtor.ser_num_pass)

    services_storage.add_passports_for_requests(
        service=service,
        task_file_verification_id=task_file_verification_id,
        passports_for_requests=passports_for_request
    )

    num_persons_for_request = len(passports_for_request)
    if num_persons_for_request > available_requests:
        msg = _('Not enough available requests to start service') + f" {service}, " + \
              _('needed') + f": <b style='color:#ff0000'>{num_persons_for_request}</b> | " + \
              _('available') + f": <b style='color:#ff0000'>{available_requests}</b>"
        raise FileVerificationException(message=f"{msg}")

    title = _('Data request debtors in service') + f" {service} - " + _('total debtors') + \
            f": {len(unique_passports)} | " + _('of them in database') + f": {len(persons_in_db)} | " + \
            _('selected for request') + f": {num_persons_for_request}"

    # logger.debug('start service in task start_fns_fssp_service')
    service_class = ServiceClass(service=service, filename=filename,
                                 task_file_verification_id=task_file_verification_id)
    service_class(progress=CustomProgressRecorder(self,  title=title))

    service_and_requests_errors, debtors_save_in_result_file, debtors_added_in_db \
        = services_storage.save_operation_results(
            service=service, task_file_verification_id=task_file_verification_id, filename=filename)

    result_message = "<b>" + _('Recorded in result') + f" {debtors_save_in_result_file} " + _('of debtors')
    if debtors_added_in_db:
        result_message += " | " + _('added to the database') + f" {debtors_added_in_db}"
    if service_and_requests_errors:
        result_message += " | " + _('data') + f" {service_and_requests_errors} " + _('debtors not received') + "</b>"

    translation.activate(prev_language)

    # Удаляем начальный, входящий файл
    os.remove(f'{settings.MEDIA_ROOT}/{service}/{filename}')

    # logger.debug('completed the celery task - start_fns_fssp_service')
    return {
        'service_and_requests_errors': service_and_requests_errors,
        'incorrect_data_or_duplicates': incorrect_data_or_duplicates,
        'message': result_message
    }
