from django.utils import translation
from django.core.handlers.wsgi import WSGIRequest

from services.utils import get_service_name, get_redis_key
from web_service.settings import redis_cache
from celery.result import AsyncResult
from services.tasks import start_service_fns
from django.utils.translation import gettext_lazy as _

from services.business_logic.service_key_verification import key_verification
import asyncio


class FNSservice:

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

    def __init__(self, task_file_verification_id: str, filename: str):
        self.filename = filename
        self.task_file_verify = AsyncResult(id=task_file_verification_id)

    def __call__(self, progress):
        print(self.filename)
        print(self.task_file_verify.result)

        for num, people in enumerate(self.peoples, 1):
            progress.set_progress(
                current=num,
                total=len(self.peoples),
                description='ФНС-Класс поиск данных: ' + f'{people}'
            )
            import time
            time.sleep(1)
        return f"Парсинг {len(self.peoples)} челов, успешно завершён"

#
# def requests_session(persons, bar):
#     response = []
#     with requests.session() as session:
#         for index, person in enumerate(persons):
#
#             if not person.my_INN and person.ready_for_req:
#                 try:
#                     result = session.get(person.fns_url).json()
#                 except Exception:
#                     result = {}
#                 try:
#                     person.my_INN = result.get("items")[0].get("ИНН")
#                     # int(result.get("items")[0].get("ИНН")) в excel неправильно отображается если число
#                 except Exception:
#                     person.my_INN = None
#
#                 if person.my_INN and person.my_INN.strip().isdigit():
#                     DBPerson.create(name=person.name, surname=person.surname, patronymic=person.patronymic,
#                                     date_birth=person.date_birth, ser_num_pass=person.ser_num_pass,
#                                     date_issue_pass=person.date_issue_pass, name_org_pass=person.name_org_pass,
#                                     my_INN=person.my_INN)
#                 response.append('person_found_in_fns' if person.my_INN else 'person_not_found')
#
#             else:
#                 response.append('person_found_in_db')
#
#             bar.next()
#     return response
#
#
# async def i_request(person: SessionPerson | str, bar=None) -> str | Dict:
#     # Windows ограничение на 64 одновременных асинхронных вызова, linux 100 но видимо api ФНС имеет свои ограничения поэтому установил 10
#     # connector = aiohttp.TCPConnector(limit=(60 if platform.system() == 'Windows' else 100))
#     connector = aiohttp.TCPConnector(limit=1)
#
#     async with aiohttp.ClientSession(json_serialize=ujson.dumps, connector=connector) as session:
#         try:
#             async with session.get(person.fns_url if isinstance(person, SessionPerson) else person) as response:
#                 result = await response.json()
#                 if isinstance(person, str):
#                     return result
#                 try:
#                     person.my_INN = result.get("items")[0].get("ИНН")
#                      #print(result)
#                     # int(result.get("items")[0].get("ИНН")) в excel неправильно отображается если число
#                 except Exception:
#                     #print(result) # {'items': [], 'error': 'Информация об ИНН не найдена. Рекомендуем проверить правильность введённых данных и повторить попытку поиска.'}
#                     person.my_INN = None
#
#                 if person.my_INN and person.my_INN.strip().isdigit():
#                     DBPerson.create(name=person.name, surname=person.surname, patronymic=person.patronymic,
#                                     date_birth=person.date_birth, ser_num_pass=person.ser_num_pass,
#                                     date_issue_pass=person.date_issue_pass, name_org_pass=person.name_org_pass,
#                                     my_INN=person.my_INN)
#                 if bar:
#                     bar.next()
#                 return 'person_found_in_fns' if person.my_INN else 'person_not_found'
#         except Exception as exc:
#             # print(exc)
#             # time.sleep(1)
#             bar.next()
#             return 'person_not_found'
#
#
# async def func_for_bar_next(bar) -> str:
#     bar.next()
#     return 'person_found_in_db'
#
#
# async def aio_parser(persons):
#     persons_found_in_db = 0
#     # result = []
#
#     bar_db = ChargingBar(f'{Fore.GREEN}Поиск в базе:', suffix=f'%(percent)d%%', max=len(persons))
#
#     db.connect()
#     for index, person in enumerate(persons):
#         bar_db.next()
#         person_in_db = DBPerson.select().where(DBPerson.ser_num_pass == person.ser_num_pass).get_or_none()
#         if person_in_db:
#             # print('В базе:', person_in_db.my_INN)
#             persons_found_in_db += 1
#             person.my_INN = person_in_db.my_INN
#     bar_db.finish()
#
#     print(f'\n{Fore.BLUE}Найдено ИНН: {Fore.YELLOW}{persons_found_in_db}{Fore.RESET}\n')
#
#     bar_parsing = ChargingBar(f'{Fore.GREEN}Парсинг:', suffix='%(percent)d%%', max=len(persons))
#     result = requests_session(persons, bar_parsing)
#
#     # nest_asyncio.apply()  # разрешает запуск цикла событий внутри цикла событий
#     # coroutines = [i_request(person=person, bar=bar_parsing) if (not person.my_INN and person.ready_for_req)
#     #               else func_for_bar_next(bar=bar_parsing) for person in persons]
#     # result = asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))
#
#     bar_parsing.finish()
#
#     persons_found_in_fns = result.count('person_found_in_fns')
#     # print(result) #['person_found_in_db', 'person_found_in_fns', 'person_not_found'.......]
#     db.close()
#
#     return persons_found_in_fns, persons_found_in_db
#
#
# async def bad_rows_to_file(bad_rows):
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     for it_row in bad_rows:
#         for row in it_row:
#             # print(row)
#             ws.append(row) #ws2.iter_rows(min_row=2, max_row=2, values_only=True)]
#     wb.save(BAD_result_file)
#
#
# async def file_to_data(path: str, fns_key: str):
#     bad_rows = []
#     persons = tuple()
#     sheet = openpyxl.load_workbook(path).active
#     if str(sheet.cell(row=3, column=2).value).strip() == 'Фамилия, имя, отчество Должника' and \
#         str(sheet.cell(row=3, column=4).value).strip() == 'Дата рождения Должника' and \
#             str(sheet.cell(row=3, column=5).value).strip() == 'Серия и номер паспорта' and \
#                 str(sheet.cell(row=3, column=6).value).strip() == 'Дата выдачи паспорта' and \
#                     str(sheet.cell(row=3, column=7).value).strip() == 'Наименование органа, выдавшего паспорт':
#         bad_rows.append(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
#         bad_rows.append(sheet.iter_rows(min_row=2, max_row=2, values_only=True))
#         bad_rows.append(sheet.iter_rows(min_row=3, max_row=3, values_only=True))
#         bad_rows.append(sheet.iter_rows(min_row=4, max_row=4, values_only=True))
#
#         type_file = 'reesir'
#
#     elif str(sheet.cell(row=1, column=15).value).strip() == 'ФИО заещика/Наименование ЮЛ' and \
#             str(sheet.cell(row=1, column=16).value).strip() == 'Дата рождения/ дата регистрации юр.лица' and \
#                 str(sheet.cell(row=1, column=18).value).strip() == 'Паспортные данные/ ИНН для юр.лиц' and \
#                     str(sheet.cell(row=1, column=20).value).strip() == 'Дата выдачи паспорта' and \
#                         str(sheet.cell(row=1, column=19).value).strip() == 'Кем выдан паспорт':
#
#         bad_rows.append(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
#         type_file = 'rosbank'
#
#     else:
#         return None, None, None
#
#     unique_pass = set()
#     duplicates_or_bad_value = 0
#     start_row = 5 if type_file == 'reesir' else 2
#
#     bar = ChargingBar(f'{Fore.GREEN}Загрузка файла:', suffix='%(percent)d%%', max=1+sheet.max_row-start_row)
#     for num in range(start_row, sheet.max_row+1):
#         bar.next()
#
#         fio = sheet.cell(row=num, column=2 if type_file == 'reesir' else 15).value
#         if fio:
#             fio = fio.split(' ', maxsplit=2)
#             if len(fio) == 3:
#                 surname, name, patronymic = fio
#             elif len(fio) == 2:
#                 surname, name, patronymic = fio[0], fio[1], ''
#             else:
#                 # По идее это условие невозможно в связи с maxsplit=2
#                 bad_rows.append(sheet.iter_rows(min_row=num, max_row=num, values_only=True))
#                 duplicates_or_bad_value += 1
#                 continue
#         else:
#             # Пустая ячейка ФИО
#             # duplicates_or_bad_value += 1
#             continue
#
#         date_birth = sheet.cell(row=num, column=4 if type_file == 'reesir' else 16).value
#         ser_num_pass = str(sheet.cell(row=num, column=5 if type_file == 'reesir' else 18).value).replace(' ', '')
#         date_issue_pass = sheet.cell(row=num, column=6 if type_file == 'reesir' else 20).value
#         name_org_pass = sheet.cell(row=num, column=7 if type_file == 'reesir' else 19).value
#
#         if ser_num_pass.isdigit() and len(ser_num_pass) == 10 and ser_num_pass not in unique_pass:
#             unique_pass.add(ser_num_pass)
#         else:
#             # Дублирующийся паспорт или количество цифр не равно 10
#             bad_rows.append(sheet.iter_rows(min_row=num, max_row=num, values_only=True))
#             duplicates_or_bad_value += 1
#             continue
#
#         if isinstance(date_birth, datetime):
#             date_birth = datetime.date(date_birth).strftime('%d.%m.%Y')
#         if isinstance(date_issue_pass, datetime):
#             date_issue_pass = datetime.date(date_issue_pass).strftime('%d.%m.%Y')
#
#         if name and surname and date_birth and ser_num_pass and date_issue_pass:
#             persons += SessionPerson(
#                 name, surname, patronymic, date_birth, ser_num_pass, date_issue_pass, name_org_pass, fns_key),
#         else:
#             # Отсутствует значение одного из или нескольких обязятельных полей
#             bad_rows.append(sheet.iter_rows(min_row=num, max_row=num, values_only=True))
#             duplicates_or_bad_value += 1
#
#     bar.finish()
#     if duplicates_or_bad_value > 0:
#         await bad_rows_to_file(bad_rows=bad_rows)
#     # for nnn, x in enumerate(persons):
#     #     print(nnn+1, x.surname, x.name, x.patronymic, x.date_birth,
#     #           x.ser_num_pass, x.date_issue_pass, x.name_org_pass)#, x.fns_url)
#     return persons, unique_pass, duplicates_or_bad_value
#
#
# async def data_to_file(path, result_data):
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.append(('Фамилия, имя, отчество', 'Дата рождения', 'Серия и номер паспорта',
#                'Наименование органа, выдавшего паспорт', 'Дата выдачи паспорта', 'ИНН'))
#     for i_person in result_data:
#         ws.append((f'{i_person.surname} {i_person.name} {i_person.patronymic if i_person.patronymic else ""}',
#                    i_person.date_birth, i_person.ser_num_pass, i_person.name_org_pass, i_person.date_issue_pass,
#                    i_person.my_INN))
#     wb.save(path)
#
#
#
# async def main():
#     db.connect()
#     db.create_tables([DBPerson, DBKey])
#     fns_key = DBKey.select().where(DBKey.id == 1).get_or_none()
#     fns_key = fns_key.i_key if fns_key else None
#     db.close()
#
#     # Проверка ключа
#     if not fns_key or not await key_verification(fns_key):
#         while True:
#             new_key = input(f'{Fore.RED}Введите ключ доступа к api ФНС:{Fore.RESET} ').strip()
#             if await key_verification(new_key):
#                 db.connect()
#                 DBKey.update(i_key=new_key).where(DBKey.id == 1).execute() if fns_key else DBKey.create(i_key=new_key)
#                 db.close()
#                 fns_key = new_key
#                 break
#
#     work_file = await choice_file()
#     if not work_file:
#         return
#
#     start = time.time()
#     persons, unique_line, dup_or_bad = await file_to_data(work_file, fns_key)
#
#     if persons:
#         if (len(unique_line) + dup_or_bad) - len(persons) > 0:
#             print(
#                 f'\n{Fore.BLUE}В {Fore.YELLOW}{len(persons) + dup_or_bad} {Fore.BLUE}строках файла {Fore.YELLOW}'
#                 f'{work_file} {Fore.BLUE}обнаружено {Fore.YELLOW}{dup_or_bad} {Fore.BLUE}дублей или ошибочных записей '
#                 f'-> записано в файл: {Fore.YELLOW}{BAD_result_file}\n'
#                 f'{Fore.BLUE}Выбрано строк для парсинга: {Fore.YELLOW}{len(persons)}{Fore.RESET}\n')
#         else:
#             print(
#                 f'\n{Fore.BLUE}В файле {Fore.YELLOW}{work_file} {Fore.BLUE}дублей или ошибочных записей не обнаружено, '
#                 f'количество строк {Fore.YELLOW}{len(persons)}{Fore.RESET}\n')
#
#         # print(input(f'\n{Fore.YELLOW}Чтобы начать парсинг - нажмите Enter{Fore.RESET}'))
#
#         found_inn, inn_in_db = await aio_parser(persons)
#         # found_inn, inn_in_db = 0, 0 # для тестов без парсинга
#
#         await data_to_file(result_file, persons)
#         print(f'\n{Fore.BLUE}Парсинг ИНН по {Fore.YELLOW}{len(unique_line)}{Fore.BLUE} строкам из {Fore.YELLOW}{len(persons) + dup_or_bad} {Fore.BLUE}строк файла {Fore.YELLOW}{work_file}{Fore.BLUE} завершён успешно\n'
#               f'Результат записан в файл: {Fore.YELLOW}{result_file}{Fore.BLUE}\nДобавлено: {Fore.YELLOW}{found_inn + inn_in_db} {Fore.BLUE}ИНН, из базы данных: {Fore.YELLOW}{inn_in_db}{Fore.BLUE}, по запросу к ФНС: {Fore.YELLOW}{found_inn}'
#               f'{Fore.RED if len(persons) - (found_inn + inn_in_db) else Fore.BLUE}, не найдено: {Fore.YELLOW}{len(persons) - (found_inn + inn_in_db)}{Fore.RED}{Fore.RESET}')
#
#         work_time = time.time() - start
#         print(f'{Fore.BLUE}Затраченное время: {Fore.YELLOW}{int(work_time//3600)} час {int((work_time%3600)//60)} мин {int((work_time%3600)%60)} сек{Fore.RESET}')
#
#     else:
#         print(f'{Fore.RED}Структура файла {Fore.YELLOW}{work_file} {Fore.RED}не соответствует настройкам программы{Fore.RESET}')
#
