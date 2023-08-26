import openpyxl
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from openpyxl.worksheet.worksheet import Worksheet

peoples = [
        'Мельникова Ксения Витальевна',
        'Иванова София Ивановна',
        'Буракшаева Юлия Сергеевна',
        'Фурсова Елизавета Владимировна',
        'Сапсай Иван Алексеевич',
        'Богословский Артем Михайлович',
        'Самбикина Юлия Владимировна',
        'Шпак Ангелина Эдуардовна',
        'Пименов Максим Евгеньевич',
        'Сигида Валерия Романовна',
        'Миронова Елизавета Валерьевна',
        'Безуглова Анастасия Александровна',
        'Сергеева Мария Вячеславовна',
        'Перфильева Милена Егоровна',
        'Химич Елена Сергеевна',
        'Бондина Анастасия Борисовна',
        'Лебедева Екатерина Сергеевна',
        'Мощева Алина Георгиевна',
        'Моругина Ирина Николаевна',
        'Прокопенко Алина Дмитривена',
    ]


@shared_task(bind=True, name='check_file_fields')
def check_file_fields(self, service, path_file, language=None) -> str:
    # FIXME
    from .business_logic.file_verification import Checker

    prev_language = translation.get_language()
    language and translation.activate(language)

    checker = Checker(service)
    progress_recorder = ProgressRecorder(self)

    sheet: Worksheet = openpyxl.load_workbook(path_file).active
    for num, (field, data) in enumerate(checker.fields_table.items(), 1):
        progress_recorder.set_progress(
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


@shared_task(bind=True, name='start_service_fns')
def start_service_fns(self, filename: str, task_file_verification_id: str, language=None) -> str:
    # FIXME
    from services.business_logic.fns_service import FNSservice
    prev_language = translation.get_language()
    language and translation.activate(language)

    fns_service = FNSservice(task_file_verification_id, filename)
    result = fns_service(progress=ProgressRecorder(self))

    translation.activate(prev_language)
    return result


@shared_task(bind=True, name='start_service_fssp')
def start_service_fssp(self, filename: str, task_file_verification_id: str, language=None) -> str:
    prev_language = translation.get_language()
    language and translation.activate(language)

    progress_recorder = ProgressRecorder(self)

    for num, people in enumerate(peoples, 1):
        progress_recorder.set_progress(
            current=num,
            total=len(peoples),
            description='ФССП поиск данных: ' + f'{people}'
        )
        import time
        time.sleep(1)
    translation.activate(prev_language)
    return "Парсинг успешно завершён"