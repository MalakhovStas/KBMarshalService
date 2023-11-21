from typing import List, Tuple, Union, Optional, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from .base_classes import BaseButton, BaseMessage
from ..config import FACE_BOT, DEFAULT_FEED_ANSWER
from ..utils.states import FSMMainMenuStates


class RegenerateAIResponse(BaseButton):

    def _set_name(self) -> str:
        return '🔁 \t Сгенерировать другой вариант'

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    def _set_children(self) -> List:
        return [
            self, SubmitForRevisionTaskQuestionOpenAI(new=False),
            CreateNewTaskForQuestionOpenAI(new=False)
        ]

    async def _set_answer_logic(self, update: CallbackQuery,
                                state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        user_id = update.from_user.id
        reply_text = self.default_i_generate_text
        wait_msg = await self.bot.send_message(chat_id=user_id, text=self.default_generate_answer)

        if ai_messages_data := await self.button_search_and_action_any_collections(
                user_id=user_id, action='get', button_name='ai_messages_data', updates_data=True):

            # выкидывает последнюю генерацию
            ai_messages_data.pop(-1)
            # получает задание - prompt
            task_to_generate_ai = ai_messages_data.pop(-1).get('content')

            ai_answer = await self.ai.some_question(
                prompt=task_to_generate_ai,
                messages_data=ai_messages_data,
                user_id=user_id,
                update=update
            )
        else:
            ai_answer = DEFAULT_FEED_ANSWER

        if ai_answer != DEFAULT_FEED_ANSWER:
            reply_text = reply_text + ai_answer + ':ai:some_question'
        else:
            self.children_buttons = []
            reply_text = self.reply_text

        await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

        return reply_text, self.next_state


class MessageOnceForSubmitForRevisionTaskQuestionOpenAIButton(BaseMessage):
    def _set_state_or_key(self) -> str:
        return 'FSMMainMenuStates:submit_for_revision_task_question_openai'

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [
            RegenerateAIResponse(new=False),
            SubmitForRevisionTaskQuestionOpenAI(new=False),
            CreateNewTaskForQuestionOpenAI(new=False)
        ]

    async def _set_answer_logic(
            self, update: Message, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        reply_text = self.default_i_generate_text
        user_id = update.from_user.id
        task_to_revision_regenerate_ai = update.text.strip()

        ai_messages_data = await self.button_search_and_action_any_collections(
            user_id=user_id, action='get', button_name='ai_messages_data', updates_data=True)

        wait_msg = await self.bot.send_message(chat_id=user_id, text=self.default_generate_answer)

        ai_answer = await self.ai.some_question(
            prompt=task_to_revision_regenerate_ai,
            messages_data=ai_messages_data,
            user_id=user_id, update=update
        )

        if ai_answer != DEFAULT_FEED_ANSWER:
            reply_text = reply_text + ai_answer + ':ai:some_question'

        else:
            self.children_buttons = []
            reply_text = self.reply_text

        await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

        return reply_text, self.next_state


class SubmitForRevisionTaskQuestionOpenAI(BaseButton):
    def _set_name(self) -> str:
        return '🗒 \t  Отправить на доработку'

    def _set_reply_text(self) -> str:
        return FACE_BOT + ' Напишите, что именно нужно доработать?' \
                          '\n\n<b>Пример:</b> Укажи больше информации о природе'

    def _set_next_state(self) -> str:
        return FSMMainMenuStates.submit_for_revision_task_question_openai

    def _set_messages(self) -> Dict:
        message = MessageOnceForSubmitForRevisionTaskQuestionOpenAIButton(
            parent_name=self.class_name
        )
        return {message.state_or_key: message}


class CreateNewTaskForQuestionOpenAI(BaseButton):
    """Кнопка старта нового задани"""

    def _set_name(self) -> str:
        return '📝 \t Новое задание'

    async def _set_answer_logic(
            self, update, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        logic_button = QuestionOpenAI(new=False)
        return logic_button.reply_text, logic_button.next_state


class MessageOnceForQuestionOpenAIButton(BaseMessage):
    """Формирует ответ на вопрос заданный OpenAI"""

    def _set_state_or_key(self) -> str:
        return 'FSMMainMenuStates:question_openai'

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [
            RegenerateAIResponse(parent_name=self.class_name, parent_button=self),
            SubmitForRevisionTaskQuestionOpenAI(parent_name=self.class_name, parent_button=self),
            CreateNewTaskForQuestionOpenAI(parent_name=self.class_name, parent_button=self)
        ]

    async def _set_answer_logic(
            self, update: Message, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        self.children_buttons = [
            RegenerateAIResponse(new=False),
            SubmitForRevisionTaskQuestionOpenAI(new=False),
            CreateNewTaskForQuestionOpenAI(new=False)
        ]
        reply_text = self.default_i_generate_text
        user_id = update.from_user.id
        task_to_generate_ai = update.text.strip()
        wait_msg = await self.bot.send_message(chat_id=user_id, text=self.default_generate_answer)

        ai_messages_data = await self.button_search_and_action_any_collections(
            user_id=user_id, action='add', button_name='ai_messages_data',
            instance_button=list(), updates_data=True)

        ai_answer = await self.ai.some_question(
            prompt=task_to_generate_ai,
            messages_data=ai_messages_data,
            user_id=user_id,
            update=update
        )

        if ai_answer != DEFAULT_FEED_ANSWER:
            reply_text = reply_text + ai_answer + ':ai:some_question'

        else:
            self.children_buttons = []
            reply_text = self.reply_text

        await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

        return reply_text, self.next_state


class QuestionOpenAI(BaseButton):
    """Класс описывающий кнопку - Задать вопрос OpenAI"""

    def _set_name(self) -> str:
        return '🙋 \t Задать вопрос OpenAI'  # ✍

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Напишите Ваш вопрос?' \
                          '\n\n<b>Пример:</b> Напиши сочинение на тему как я провёл лето.'

    def _set_next_state(self) -> str:
        return FSMMainMenuStates.question_openai

    def _set_messages(self) -> Dict:
        message = MessageOnceForQuestionOpenAIButton(parent_name=self.class_name)
        return {message.state_or_key: message}
