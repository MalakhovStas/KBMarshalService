from typing import Tuple, Optional, List

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async

from services.views import BaseServicesPageView
from users.models import User
from .base_classes import BaseButton
from .base_classes import Utils, GoToBack
from ..config import FACE_BOT


async def fns_fssp_services_logic(update: CallbackQuery, service_name: str) -> str:
    """Общая логика получения информации от сервисов ФНС и ФССП"""
    user = await User.objects.filter(tg_user_id=update.from_user.id).afirst()

    context = BaseServicesPageView.get_context_logic(service=service_name, user=user.pk)
    # {'service': 'FNS', 'filename': None, 'task_file_verification': None,
    #  'task_start_service': None}

    if (task_file_verification := context.get('task_file_verification')) and (
            task_file_verification_result := await sync_to_async(
                task_file_verification._get_task_meta, thread_sensitive=True)()):

        # print(task_file_verification_result)

        reply_text = (f"<b>Загрузка файла завершена:</b> "
                      f"{'УСПЕШНО' if task_file_verification_result.get('status') else 'НЕ УСПЕШНО'}\n")
        reply_text += f"\n<b>Сервис {service_name}:</b> "

        if (task_start_service := context.get('task_start_service')) and (
                task_start_service_result := await sync_to_async(
                    task_start_service._get_task_meta, thread_sensitive=True)()):
            # print(task_start_service_result)

            if status := task_start_service_result.get('status'):
                if status in ['SUCCESS', 'FAILURE']:
                    reply_text += (f"обработка завершена - "
                                   f"{'успешно' if status else 'не успешно'}\n")
                    if (result := task_start_service_result.get('result')) and (
                            message := result.get('message')):
                        reply_text += f"\n{message}"
                elif status in ['PROGRESS']:
                    if result := task_start_service_result.get('result'):
                        if percent := result.get('percent'):
                            reply_text += f" в процессе, завершено - {int(percent)}%\n"
                        if title := result.get('title'):
                            reply_text += f"\n{title}"
        else:
            reply_text += f"обработка - не запускалась"
    else:
        reply_text = f"<b>Сервис {service_name}:</b> - нет активных задач"
    return reply_text


class UpdateData(BaseButton, Utils):
    def _set_name(self) -> str:
        return '🌐 Обновить информацию'

    def _set_reply_text(self) -> Optional[str]:
        return "Ошибка обновления данных - обратитесь в поддержку"

    async def _set_answer_logic(
            self, update: CallbackQuery, state: FSMContext) -> Tuple[str, Optional[str]]:
        reply_text, next_state = self.reply_text, self.next_state
        data = await state.get_data()
        if service_button := await self.button_search_and_action_any_collections(
                user_id=update.from_user.id, action='get',
                button_name=data.get('previous_button')):
            if hasattr(service_button.__class__, '_set_answer_logic'):
                reply_text, next_state = await service_button._set_answer_logic(update, state)
            else:
                reply_text, next_state = service_button.reply_text, service_button.next_state
            self.children_buttons = service_button.children_buttons
        return reply_text, next_state


class ServiceFNS(BaseButton, Utils):
    """Кнопка ФНС сервис"""
    service = 'FNS'

    def _set_name(self) -> str:
        return 'ФНС сервис'  # 🔑 🔐 🗝

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + ('<b>Ошибка получения информации от сервиса ФНС. '
                           'Обратитесь в поддержку.</b>')

    def _set_children(self) -> List:
        return [UpdateData(), GoToBack(new=False)]

    async def _set_answer_logic(self, update: CallbackQuery, state: FSMContext) -> Tuple:
        reply_text = await fns_fssp_services_logic(update=update, service_name=self.service)
        if not reply_text:
            reply_text = self.reply_text
        return reply_text, self.next_state


class ServiceFSSP(BaseButton, Utils):
    """Кнопка ФССП сервис"""
    service = 'FSSP'

    def _set_name(self) -> str:
        return 'ФССП сервис'  # 🔑 🔐 🗝

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + ('<b>Ошибка получения информации от сервиса ФССП. '
                           ' Обратитесь в поддержку.</b>')

    def _set_children(self) -> List:
        return [UpdateData(new=False), GoToBack(new=False)]

    async def _set_answer_logic(self, update: CallbackQuery, state: FSMContext) -> Tuple:
        reply_text = await fns_fssp_services_logic(update=update, service_name=self.service)
        if not reply_text:
            reply_text = self.reply_text
        return reply_text, self.next_state


class ServicesMenu(BaseButton):
    """Класс описывающий кнопку - Сервисы"""

    def _set_name(self) -> str:
        return '🔐 Сервисы'

    def _set_reply_text(self) -> str:
        return self.default_choice_menu

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [
            ServiceFNS(parent_name=self.class_name),
            ServiceFSSP(parent_name=self.class_name),
        ]
