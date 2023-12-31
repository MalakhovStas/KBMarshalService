from datetime import datetime
from typing import Union, Dict, Tuple

from services import utils


class BaseField:
    """
    В заголовке столбца должны быть слова из переменных:
    words_to_search_in_title или or_words_to_search_in_title
    и в первых 30 ячейках должно быть хотя-бы одно валидное
    значение согласно логике подкласса соответствующего искомой колонке
    """

    words_to_search_in_title = []
    or_words_to_search_in_title = []

    def check_title(self, cell_value: str, column) -> Union[bool, Dict]:
        result = False
        cell_value = cell_value.lower()
        if all([word in cell_value for word in self.words_to_search_in_title]) or \
                (self.or_words_to_search_in_title and
                 all([word in cell_value for word in self.or_words_to_search_in_title])):
            result = {'column': column}
        return result

    def get_data(self, cell_value: str):
        pass

    def check_data(self, cell_value: str, row) -> Union[bool, Dict]:
        result = False
        if any(self.get_data(cell_value=cell_value)):
            result = {'row': row}
        return result


class IdCreditPerson(BaseField):
    """Подкласс поиска колонки - id кредит"""
    words_to_search_in_title = ['id', 'кредит']
    or_words_to_search_in_title = ['id', 'кредита']

    def get_data(self, cell_value: str) -> Tuple:
        id_credit = False
        cell_value = cell_value.replace(' ', '')
        if cell_value.isdigit():
            id_credit = cell_value
        return (id_credit,)


class FullNamePerson(BaseField):
    """Подкласс поиска колонки - ФИО"""
    words_to_search_in_title = ['фамилия', 'имя', 'отчество']
    or_words_to_search_in_title = ['фио']

    def get_data(self, cell_value: str) -> Tuple:
        surname, name, patronymic = None, None, None
        if cell_value:
            cell_value = cell_value.split(' ', maxsplit=2)
            if 1 < len(cell_value) <= 3 and all([word.isalpha() for word in cell_value]):
                if len(cell_value) == 3:
                    surname, name, patronymic = cell_value
                elif len(cell_value) == 2:
                    surname, name, patronymic = cell_value[0], cell_value[1], ''
        return surname, name, patronymic


class DateBirthPerson(BaseField):
    """Подкласс поиска колонки - дата рождения"""
    words_to_search_in_title = ['дата', 'рождения']
    min_age_person = 18

    def get_data(self, cell_value: str) -> Tuple:
        result = False
        if cell_value:
            date_birth_string, date_birth_datetime = utils.date_identifier_and_converter(cell_value)
            if date_birth_datetime and (
                    (datetime.now() - date_birth_datetime).days + 5) / 365 >= self.min_age_person:
                result = date_birth_string
        return (result,)


class SerNumPassport(BaseField):
    """Подкласс поиска колонки - серия номер паспорта"""
    words_to_search_in_title = ['паспортные', 'данные']
    or_words_to_search_in_title = ['серия', 'номер', 'паспорта']
    max_years_after_date_issue = 30

    def get_data(self, cell_value: str) -> Tuple:
        result = False
        cell_value = cell_value.replace(' ', '')
        if cell_value.isdigit() and len(cell_value) == 10:
            result = cell_value
        return (result,)


class DateIssuePassport(BaseField):
    """Подкласс поиска колонки - дата выдачи паспорта"""
    words_to_search_in_title = ['дата', 'выдачи', 'паспорта']
    or_words_to_search_in_title = ['дата', 'выдачи', 'паспорт']
    max_years_after_date_issue = 30

    def get_data(self, cell_value: str) -> Tuple:
        result = False
        if cell_value:
            if cell_value:
                date_issue_string, date_issue_datetime = utils.date_identifier_and_converter(cell_value)
                if date_issue_datetime and (
                        datetime.now() - date_issue_datetime).days / 365 <= self.max_years_after_date_issue:
                    result = date_issue_string
        return (result,)


class NameOrgIssuePassport(BaseField):
    """Подкласс поиска колонки - кем выдан паспорт"""
    words_to_search_in_title = ['кем', 'выдан', 'паспорт']
    or_words_to_search_in_title = ['наименование', 'органа', 'выдавшего', 'паспорт']

    def get_data(self, cell_value: str) -> Tuple:
        result = False
        if cell_value:
            result = cell_value
        return (result,)


class INN(BaseField):
    """Подкласс поиска колонки - ИНН"""
    words_to_search_in_title = ['инн']
    or_words_to_search_in_title = ['индивидуальный', 'номер', 'налогоплательщика']
    num_digits_inn_people = 12
    num_digits_inn_company = 10

    def get_data(self, cell_value: str) -> Tuple:
        result = False
        cell_value = cell_value.replace(' ', '')
        if cell_value.isdigit() and len(cell_value) == self.num_digits_inn_people:
            result = cell_value
        return (result,)
