from typing import Optional, List, Dict, Tuple

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from debtors.models import Debtor
from utils import utils
from .base_classes import BaseButton, BaseMessage, GoToBack
from ..config import FACE_BOT
from ..utils.states import FSMMainMenuStates


class MessageGetDebtor(BaseMessage):
    def _set_state_or_key(self) -> str:
        return 'FSMMainMenuStates:get_debtor'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Информация о должнике не найдена</b>'

    def _set_next_state(self) -> Optional[str]:
        return 'reset_state'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    @staticmethod
    def get_isp_prs(debtor: Debtor) -> str:
        """Возвращает подготовленную строку исполнительных производств"""
        result = ''
        if debtor.isp_prs and isinstance(debtor.isp_prs, dict):
            for num, (key, value) in enumerate(debtor.isp_prs.items(), 1):
                if len(str(debtor.isp_prs)) > 3700:
                    result += f'\n{num}. {key}\n'
                else:
                    result += f'\n<b>{num}. {key}</b>\n'
                for field_name, field_data in value.items():
                    result += f'{field_name}: {field_data}\n'
        return result

    async def _set_answer_logic(
            self, update: Message, state: Optional[FSMContext] = None) -> Tuple:
        reply_text = self.reply_text
        debtor = None
        if search_query := update.text:
            search_query = search_query.strip().lower()
            surname, name, patronymic = utils.get_fullname(search_query)
            if surname and name and patronymic:
                debtor = await Debtor.objects.filter(
                    surname=surname, name=name, patronymic=patronymic).afirst()
            elif surname and name:
                debtor = await Debtor.objects.filter(surname=surname, name=name).afirst()
            elif surname:
                debtor = await Debtor.objects.filter(surname=surname).afirst()
            elif passport := utils.get_passport(search_query):
                debtor = await Debtor.objects.filter(ser_num_pass=passport).afirst()
            elif inn := utils.get_inn(search_query):
                debtor = await Debtor.objects.filter(inn=inn).afirst()
            elif id_credit := utils.get_id_credit(search_query):
                debtor = await Debtor.objects.filter(id_credit=id_credit).afirst()

            if debtor:
                isp_prs = self.get_isp_prs(debtor=debtor)
                reply_text = f"<b>{FACE_BOT}Информация о должнике:</b>\n\n"
                reply_text += f"<b>Id кредит:</b> {debtor.id_credit}\n" if debtor.id_credit else ""
                reply_text += f"<b>Фамилия:</b> {debtor.surname}\n"
                reply_text += f"<b>Имя:</b> {debtor.name}\n"
                reply_text += f"<b>Отчество:</b> {debtor.patronymic}\n" if debtor.patronymic else ""
                reply_text += f"<b>Дата рождения:</b> {debtor.date_birth.strftime('%d.%m.%Y')}\n" if debtor.date_birth else ""
                reply_text += f"<b>ИНН:</b> {debtor.inn}\n" if debtor.inn else ""
                reply_text += f"<b>Серия номер паспорта:</b> {debtor.ser_num_pass}\n"
                reply_text += f"<b>Дата выдачи паспорта:</b> {debtor.date_issue_pass.strftime('%d.%m.%Y')}\n" if debtor.date_issue_pass else ""
                reply_text += f"<b>Кем выдан паспорт:</b> {debtor.name_org_pass}\n" if debtor.name_org_pass else ""
                reply_text += f"\n<b>Исполнительное производство:</b>{isp_prs}" if isp_prs else ""

            self.children_buttons = []
        return reply_text, self.next_state


class GetDebtors(BaseButton):
    """Класс описывающий кнопку - Должники"""

    def _set_name(self) -> str:
        return '💰 \t Должники'

    def _set_reply_text(self) -> str:
        return f"{FACE_BOT} Для поиска должника введите\n<b>ФИО | ИНН | Паспорт | Id кредит</b>"

    def _set_next_state(self) -> Optional[str]:
        return FSMMainMenuStates.get_debtor

    def _set_messages(self) -> Dict:
        messages = [MessageGetDebtor(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}
