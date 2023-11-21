"""Модуль предварительной и постобработки входящих сообщений"""
from typing import Dict, Optional, List

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from users.models import User
from ..config import FLOOD_CONTROL, FLOOD_CONTROL_STOP_TIME
from ..loader import bot, security, dbase, Base
from ..utils import exception_control


class AccessControlMiddleware(BaseMiddleware):
    """Класс предварительной обработки входящих сообщений для защиты от нежелательной нагрузки
    и постобработки"""
    dbase = dbase
    bot = bot
    security = security

    def __init__(self) -> None:
        super().__init__()
        self.sign = self.__class__.__name__ + ': '

    @exception_control.exception_handler_wrapper
    async def on_pre_process_update(self, update: Update, update_data: Dict) -> None:
        command = None
        if update.message:
            command = update.message.get_command()

        update = update.message if update.message else update.callback_query
        # print(update)
        # print(update.message.reply_markup.values.get('inline_keyboard')[0][0].text[-7:])
        # print(Base.general_collection)
        user = await User.objects.filter(tg_user_id=update.from_user.id).afirst()
        if not user:
            if command == '/start' and len((command_list := update.text.split())) >= 2:
                code = command_list[1]
                if new_user := await User.objects.filter(code_tg_register_link=code).afirst():
                    new_user.tg_user_id = update.from_user.id
                    new_user.first_name = update.from_user.first_name
                    new_user.tg_username = update.from_user.username
                    await new_user.asave()
                else:
                    raise CancelHandler()
            else:
                raise CancelHandler()

        user_data = self.manager.storage.data.get(str(update.from_user.id))
        if isinstance(update, CallbackQuery):
            await self.bot.answer_callback_query(callback_query_id=update.id)

        if not await self.security.check_user(update, user_data):
            raise CancelHandler()

        text_last_request = "Message: " + str(update.text) if isinstance(
            update, Message) else "Callback: " + str(update.data)
        await self.dbase.update_last_request_data(
            update=update, text_last_request=text_last_request)

        if FLOOD_CONTROL:
            control = await self.security.flood_control(update)
            if control in ['block', 'bad', 'blocked']:
                if control != 'blocked':
                    text = {'block': f'&#129302 Доступ ограничен на '
                                     f'{FLOOD_CONTROL_STOP_TIME} секунд',
                            'bad': '&#129302 Не так быстро пожалуйста'}
                    await bot.send_message(chat_id=update.from_user.id, text=text[control])
                raise CancelHandler()
        from ..handlers import handlers

    @exception_control.exception_handler_wrapper
    async def on_process_update(self, update: Update, update_data: Dict) -> Optional[Dict]:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_update(self, update: Update, post: List, update_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_pre_process_message(self, message: Message, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_process_message(self, message: Message, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_message(
            self, message: Message, post: List, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_pre_process_callback_query(
            self, call: CallbackQuery, callback_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_process_callback_query(self, call: CallbackQuery, callback_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_callback_query(
            self, call: CallbackQuery, post: List, callback_data: Dict) -> None:
        data = callback_data.get('state')
        if not call.data in ['UpdateData']:#, 'GoToBack']:
            await data.update_data(previous_button=call.data)
            await Base.button_search_and_action_any_collections(
                user_id=call.from_user.id, action='add',
                button_name='previous_button', instance_button=call.data, updates_data=True)
