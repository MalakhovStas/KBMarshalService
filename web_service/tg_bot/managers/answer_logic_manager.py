from typing import Any, Optional, List, Union, Tuple

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..buttons_and_messages.main_menu import MainMenu


class AnswerLogicManager:
    """ Класс Singleton для работы с API Wildberries и соблюдения принципа DRY """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, bot, ai, logger):
        self.sign = self.__class__.__name__ + ': '
        self.main = MainMenu()
        self.bot = bot
        self.ai = ai
        self.logger = logger

    async def create_keyboard(
            self,
            buttons: Optional[List],
            insert: bool = False,
            main_menu: bool = False,
            parent_button: Optional[Any] = None) -> InlineKeyboardMarkup:
        """Метод создания клавиатуры"""

        parent_button = self.main if not parent_button else parent_button

        if buttons == self.main.children_buttons:
            main_menu = False
            insert = True

        # if not parent_button or parent_button == self.main:
        #     insert = True
        #     main_menu = True

        keyboard = InlineKeyboardMarkup()
        if buttons:
            for index, button in enumerate(buttons, 1):
                button_name = button.name
                if button.class_name == 'CreateNewTaskForResponseManually':
                    insert = True

                if button.class_name == 'GoToBack':
                    main_menu = True
                    insert = True

                if len(buttons) == 1 or index < len(buttons):
                    keyboard.add(InlineKeyboardButton(
                        text=button_name, callback_data=button.callback, url=button.url))
                else:
                    keyboard.insert(InlineKeyboardButton(
                        text=button_name, callback_data=button.callback, url=button.url)) \
                        if insert and not main_menu else keyboard.add(InlineKeyboardButton(
                            text=button_name, callback_data=button.callback, url=button.url))

        if main_menu:
            main_inline_button = InlineKeyboardButton(
                text=self.main.name, callback_data=self.main.callback)
            keyboard.insert(main_inline_button) if insert else keyboard.add(main_inline_button)

        return keyboard

    async def get_reply(
            self,
            update: Union[Message, CallbackQuery, None] = None,
            state: Optional[FSMContext] = None,
            button: Optional[Any] = None,
            message: Optional[Any] = None,
            insert: bool = False,
            main_menu: bool = True,
            not_keyboard: bool = False
    ) -> Tuple[Optional[str], Optional[InlineKeyboardMarkup], Optional[str]]:
        """Получить ответ"""
        buttons = None
        current_data = {}
        current_state = None

        if state:
            current_data = await state.get_data()
            current_state = await state.get_state()

        if isinstance(update, CallbackQuery):
            if button := await self.main.button_search_and_action_any_collections(
                    user_id=update.from_user.id, action='get', button_name=update.data):
                buttons = button.children_buttons

        elif isinstance(update, Message):
            if update.get_command() == '/start':
                message = None
                button = self.main
                buttons = button.children_buttons

            else:
                if message := await self.main.button_search_and_action_any_collections(
                        action='get', button_name=current_state, message=True):
                    buttons = message.children_buttons

        if not button and not message:
            """Если нет никаких данных всегда возвращает главное меню например по команде /start"""
            button = self.main
            buttons = button.children_buttons

        if button is self.main:
            # Вывод всех кнопок главного меню
            main_menu = False
            insert = True

        if message:
            main_menu = True
            if hasattr(message.__class__, '_set_answer_logic'):
                reply_text, next_state = await message._set_answer_logic(update, state)
                if hasattr(message, 'children_buttons'):
                    buttons = message.children_buttons
            else:
                reply_text, next_state = message.reply_text, message.next_state

            if reply_text == message.default_incorrect_data_input_text:
                main_menu = False

        else:
            if hasattr(button, 'children_buttons'):
                buttons = button.children_buttons

            if hasattr(button.__class__, '_set_answer_logic'):
                reply_text, next_state = await button._set_answer_logic(update, state)
                if hasattr(button, 'children_buttons'):
                    buttons = button.children_buttons

            else:
                reply_text, next_state = button.reply_text, button.next_state

        parent_button = button.parent_button if button else None

        if button and button.class_name == 'CallGetBalance':
            insert = True

        if not_keyboard:
            keyboard = None
        else:
            keyboard = await self.create_keyboard(
                buttons=buttons,
                insert=insert,
                main_menu=main_menu,
                parent_button=parent_button,
            )
        return reply_text, keyboard, next_state
