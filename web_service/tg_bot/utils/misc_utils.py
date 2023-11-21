"""Модуль дополнительных инструментов"""
import re
from random import choice
from typing import Any, Union, Optional, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

""" Отображаемое кол-во отзывов на кнопке supplier 'all' / '99+' """
NUM_FEEDS_ON_SUPPLIER_BUTTON = '99+'
# NUM_FEEDS_ON_SUPPLIER_BUTTON = 'all'


def set_button_name(button_id: Union[str, int]) -> str:
    """ Не асинхронный метод вызывается из __call__ """
    if isinstance(button_id, int):
        button_id = str(button_id)

    # long_btn_id -> 0000058
    long_btn_id = button_id.zfill(7)
    # return start_name[:-7] + long_btn_id, long_btn_id
    return long_btn_id


async def check_data(data: str) -> Optional[str]:
    """Удаляет из строки data все символы из table_symbols на выходе только цифры или None"""
    ru_alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    en_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    any_symbols = ' ~`"\'@#№$:;.,%^&?*|()[]{}-=+<>/\\'
    table_symbols = ''.join([*ru_alphabet, *en_alphabet, *any_symbols])

    for sym in table_symbols:
        data = data.replace(sym, '')
    return data if data.isdigit() else None


async def change_name_button(button, num: Optional[int] = None, minus_one: bool = False):
    """ Изначальное имя кнопки задаётся тут ->  buttons_and_messages/base_classes.py:979 """
    i_was = None
    res_re = re.search(r'〔 \d+ 〕', button.name)
    if res_re:
        i_was = res_re.group(0)
    was = i_was if i_was else '〔 0 〕'

    if minus_one:
        num = int(was.strip('〔〕 ')) - 1

    if NUM_FEEDS_ON_SUPPLIER_BUTTON == '99+':
        button.name = button.name.replace(was, f'〔 {NUM_FEEDS_ON_SUPPLIER_BUTTON} 〕') if num > 99 \
            else button.name.replace(was, f'〔 {num} 〕')
    else:
        button.name = button.name.replace(was, f'〔 {num} 〕')
    return button


async def create_keyboard(button: Any) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру из одной кнопки"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=button.name, callback_data=button.class_name))
    return keyboard


async def random_choice_dict_elements(is_dict: Dict, num_elements: int) -> Dict:
    result_dict = dict()
    if len(is_dict) > num_elements:
        while len(result_dict) < num_elements:
            key = choice(list(is_dict.keys()))
            result_dict.update({key: is_dict[key]})
    else:
        result_dict = is_dict
    return result_dict
