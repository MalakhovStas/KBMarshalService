import re
import random
from typing import Tuple, Union, Optional
import string

def get_fullname(search_query: str) -> Tuple:
    """Выделяет из строки имя, фамилию, отчество разделённые пробелом"""
    surname, name, patronymic = None, None, None
    if search_query:
        search_query = search_query.split(' ', maxsplit=2)
        if 0 < len(search_query) <= 3 and all([word.isalpha() for word in search_query]):
            if len(search_query) == 3:
                surname, name, patronymic = search_query
            elif len(search_query) == 2:
                surname, name, patronymic = search_query[0], search_query[1], ''
            elif len(search_query) == 1:
                surname, name, patronymic = search_query[0], None, None
    surname = surname.lower().title() if isinstance(surname, str) else surname
    name = name.lower().title() if isinstance(name, str) else name
    patronymic = patronymic.lower().title() if isinstance(patronymic, str) else patronymic
    return surname, name, patronymic


def get_passport(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 10:
        result = search_query
    return result


def get_inn(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 12:
        result = search_query
    return result


def get_id_credit(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) < 10:
        result = search_query
    return result

def get_phone_number(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) < 10:
        result = search_query
    return result


async def data_to_str_digits(data: str) -> Optional[str]:
    """Удаляет из строки data все символы из table_symbols на выходе только цифры или None"""
    ru_alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    en_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    any_symbols = ' ~`"\'@#№$:;.,%^&?*|()[]{}-=+<>/\\'
    table_symbols = ''.join([*ru_alphabet, *en_alphabet, *any_symbols])

    for sym in table_symbols:
        data = data.replace(sym, '')
    return data if data.isdigit() else None


async def data_to_phone(data: str) -> Optional[str]:
    """Выделяет из строки символов цифры проверяет их количество, если == 11,
    возвращает набор цифр, в противном случае None"""
    result = None
    numbers = await data_to_str_digits(data)
    if numbers and len(numbers) == 11:
        result = numbers
    return result


async def data_to_email(data: str) -> Optional[str]:
    """Проверяет email на соответствие паттерну регулярного выражения,
    возвращает введённый email, в противном случае None"""
    result = None
    # pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, data) is not None:
        result = data
    return result


def make_code_tg_register_link():
    """Формирует строку случайных неповторяющихся символов длиной length"""
    length = 32
    dictionary = string.digits + string.ascii_letters
    return "".join(random.sample(dictionary, length))
