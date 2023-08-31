import openpyxl
from celery import shared_task
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from openpyxl.worksheet.worksheet import Worksheet

from debtors.models import Debtor
from services.business_logic.custom_progress import CustomProgressRecorder
from services.business_logic.exceptions import FileVerificationException
from services.business_logic.file_reader import FileReader
from services.business_logic.loader import services_storage
from services.business_logic.fns_service import ServiceClass


@shared_task(bind=True, name='check_file_fields')
def check_file_fields(self, service, filename, language=None) -> str:
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
    return result


@shared_task(bind=True, name='start_fns_fssp_service')
def start_fns_fssp_service(self, service, filename: str, task_file_verification_id: str,
                           available_requests: int, language=None) -> str:
    prev_language = translation.get_language()
    language and translation.activate(language)

    file_reader = FileReader(service, task_file_verification_id, filename)
    unique_passports, duplicates_or_bad_value = file_reader(
        progress=CustomProgressRecorder(self, title=_('File data loading'))
    )

    persons_in_db = Debtor.objects.in_bulk(unique_passports, field_name='ser_num_pass')
    passports_for_request = [passport for passport in unique_passports if passport not in persons_in_db.keys()]
    num_persons_for_request = len(passports_for_request)

    for passport_in_db in persons_in_db:
        services_storage.delete(
            service=service,
            task_file_verification_id=task_file_verification_id,
            passport=passport_in_db
        )

    services_storage.add_passports_for_requests(
        service=service,
        task_file_verification_id=task_file_verification_id,
        passports_for_requests=passports_for_request
    )

    if num_persons_for_request > available_requests:
        msg = (
            f"{_('Not enough available requests to start service')} {service}, "
            f"{_('needed')}: <b style='color:#ff0000'>{num_persons_for_request}</b> | "
            f"{_('available')}: <b style='color:#ff0000'>{available_requests}</b>"
        )
        raise FileVerificationException(message=f"{msg}")

    title = f"{_('Data request debtors in service')} {service} - {_('total debtors')}: {len(unique_passports)} | " \
            f"{_('of them in database')}: {len(persons_in_db)} | " \
            f"{_('selected for request')}: {num_persons_for_request}"

    service_class = ServiceClass(
        service=service, filename=filename, task_file_verification_id=task_file_verification_id)
    service_class(progress=CustomProgressRecorder(self,  title=title))

    not_found, added_in_db = services_storage.save_operation_results(
        service=service, task_file_verification_id=task_file_verification_id, filename=filename)

    translation.activate(prev_language)
    return f"<b>{added_in_db} {_('debtors added to the database')} |" \
           f" {_('data on')} {not_found} {_('debtors not received')}</b>"
