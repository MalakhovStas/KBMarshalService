from datetime import datetime
from typing import Generator

from celery.result import AsyncResult
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from services.business_logic.exceptions import FileVerificationException
from services.business_logic.file_verification_fields_models import FullNamePerson, DateBirthPerson, \
    DateIssuePassport, SerNumPassport, NameOrgIssuePassport, INN
from services.tasks import check_file_fields
from services.utils import get_redis_key, get_service_name
from web_service.settings import redis_cache


class Checker:
    """ Проверяет файл на наличие столбцов """
    rows_for_check = 30
    max_title_row = 10

    trans_fields = {
        'fullname': _('Fullname'),
        'date_birth': _('Date birth'),
        'ser_num_pass': _('Serial and passport number'),
        'date_issue_pass': _('Date issue passport'),
        'name_org_pass': _('Passport issued by'),
        'inn': _('INN'),
    }

    def __init__(self, service: str):
        self.service = service
        self.fields_table = {
            'fullname': {'column': None, 'row': None, 'class_field': FullNamePerson()},
            'date_birth': {'column': None, 'row': None, 'class_field': DateBirthPerson()},
            'ser_num_pass': {'column': None, 'row': None, 'class_field': SerNumPassport()},
            'date_issue_pass': {'column': None, 'row': None, 'class_field': DateIssuePassport()},
            'name_org_pass': {'column': None, 'row': None, 'class_field': NameOrgIssuePassport()},
        }
        if self.service == "FSSP":
            self.fields_table.update({'inn': {'column': None, 'row': None, 'class_field': INN()}})
        self.detected_columns = set()

    def check_field(self, field, title_row, column, sheet) -> bool:
        class_field = self.fields_table[field]['class_field']
        cell_value = str(sheet.cell(row=title_row, column=column).value).strip()
        if result_column := class_field.check_title(cell_value=cell_value, column=column):
            for data_row in range(
                    self.rows_for_check if sheet.max_row >= self.rows_for_check else sheet.max_row, 1, -1):
                cell_value = str(sheet.cell(row=data_row, column=column).value).strip()
                if result_row := class_field.check_data(cell_value=cell_value, row=data_row):
                    self.fields_table[field].update({**result_column, **result_row})
        if result := all((self.fields_table[field]['column'], self.fields_table[field]['row'])):
            self.detected_columns.add(result_column['column'])
        return result

    @classmethod
    def search_title_gen(cls, max_column: int) -> Generator:
        for title_row in range(1, cls.max_title_row+1):
            for column in range(1, max_column+1):
                yield title_row, column

    def check_fields_result(self, sheet) -> str | dict:
        # try:
        f_col = self.fields_table["fullname"]["column"]
        f_row = self.fields_table["fullname"]["row"]
        fc_name = sheet.cell(row=1, column=f_col).column_letter if f_col else None

        db_col = self.fields_table["date_birth"]["column"]
        db_row = self.fields_table["date_birth"]["row"]
        dbc_name = sheet.cell(row=1, column=db_col).column_letter if db_col else None

        snp_col = self.fields_table["ser_num_pass"]["column"]
        snp_row = self.fields_table["ser_num_pass"]["row"]
        snpc_name = sheet.cell(row=1, column=snp_col).column_letter if snp_col else None

        dip_col = self.fields_table["date_issue_pass"]["column"]
        dip_row = self.fields_table["date_issue_pass"]["row"]
        dipc_name = sheet.cell(row=1, column=dip_col).column_letter if dip_col else None

        nop_col = self.fields_table["name_org_pass"]["column"]
        nop_row = self.fields_table["name_org_pass"]["row"]
        nop_name = sheet.cell(row=1, column=nop_col).column_letter if nop_col else None

        result_data = {
            'fullname': {'col': f_col, 'col_name': fc_name, 'start_row': f_row},
            'date_birth': {'col': db_col, 'col_name': dbc_name, 'start_row': db_row},
            'ser_num_pass': {'col': snp_col, 'col_name': snpc_name, 'start_row': snp_row},
            'date_issue_pass': {'col': dip_col, 'col_name': dipc_name, 'start_row': dip_row},
            'name_org_pass': {'col': nop_col, 'col_name': nop_name, 'start_row': nop_row},
        }

        # Дата выдачи паспорта и Кем выдан паспорт - не проверяется, если нет не будет ошибки
        columns = (f_col, db_col, snp_col)

        if self.service == "FSSP":
            inn_col = self.fields_table.get("inn")["column"]
            inn_row = self.fields_table.get("inn")["row"]
            innc_name = sheet.cell(row=1, column=inn_col).column_letter if inn_col else None
            result_data.update({'inn': {'col': inn_col, 'col_name': innc_name, 'start_row': inn_row}})

            columns += (inn_col,)

        if all(columns):
            return result_data
        else:
            not_found_columns = [self.trans_fields[key] for key, value in result_data.items() if not value["col"]]
            if len(not_found_columns) > 1:
                msg = _("not found columns")
            else:
                msg = _("not found column")
            raise FileVerificationException(message=f"{msg}: <b style='color:#ff0000'>{not_found_columns}</b>")
        # except Exception as exc:
        #     FIXME убрать вывод самого исключения
            # raise FileVerificationException(
            #     message=f"<b style='color:#ff0000'>{_('An error occurred while checking a file')} error: {exc}</b>"
            # )


def load_data_file(request) -> tuple[str, AsyncResult, str]:
    service = get_service_name(request)
    date = datetime.strftime(datetime.now(), '%d.%m.%Y-%H:%M:%S')
    filename = None
    task = None

    if request.FILES:
        file: TemporaryUploadedFile | InMemoryUploadedFile = request.FILES['datafile']

        if file.name.endswith(('.xls', '.xlsx')):
            file_system = FileSystemStorage()

            filename = f'{service}-{date}-user:{request.user.pk}-filename:{file.name}'
            file_system.save(f'{service}/{filename}', file)

            task: AsyncResult = check_file_fields.delay(
                service=service,
                filename=filename,
                language=translation.get_language()
            )
            redis_cache.set(
                name=get_redis_key(request=request, task_name=f'FILE_VERIFICATION'),
                value=f'{task.task_id}:{filename}'
            )
            msg = _(f"File verification") + f": {file.name}"
        else:
            msg = _('Unsupported file, .xls .xlsx only')
    else:
        msg = _("Select File")
    return msg, task, filename
