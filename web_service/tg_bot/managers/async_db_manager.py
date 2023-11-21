import functools
from datetime import datetime
from types import FunctionType
from typing import Any, Callable, Union, Tuple, Optional, Dict

from aiogram.types import Message, CallbackQuery
from loguru import logger

from tg_bot.config import ADMINS, TECH_ADMINS
from tg_bot.database.db_utils import Tables, db

from django.conf import settings

"""Все таблицы создаются тут - потому, что таблицы должны создаваться 
раньше чем экземпляр класса DBManager, иначе 
будут ошибки при создании экземпляров классов кнопок и сообщений"""
db.create_tables(Tables.all_tables())


class DBManager:
    """ Класс Singleton надстройка над ORM "peewee" для вынесения логики сохранения данных """
    point_db_connection = db
    tables = Tables

    __instance = None
    sign = None
    logger = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.sign = cls.__name__ + ': '
            cls.logger = logger
            cls.decorate_methods()
        return cls.__instance

    def __init__(self):
        pass
        # self.logger = logger
        # sign = __class__.__name__ + ': '
        # self.decorate_methods()

    @staticmethod
    def db_connector(method: Callable) -> Callable:
        @functools.wraps(method)
        async def wrapper(*args, **kwargs) -> Any:
            with DBManager.point_db_connection:
                result = await method(*args, **kwargs)
            return result
        return wrapper

    @classmethod
    def decorate_methods(cls):
        for attr_name in cls.__dict__:
            if (not attr_name.startswith('__')
                    and attr_name not in ['db_connector', 'decorate_methods']):
                method = cls.__getattribute__(cls, attr_name)
                if type(method) is FunctionType:
                    if settings.DEBUG:
                        cls.logger.debug(cls.sign + f'decorate_methods -> db_connector '
                                                    f'wrapper -> method: {attr_name}')
                    setattr(cls, attr_name, cls.db_connector(method))

    async def get_or_create_user(
            self, update: Union[Message, CallbackQuery]) -> Tuple[Tuple, Union[bool, int]]:
        """ Если user_id не найден в таблице Users -> создаёт новые записи в
            таблицах Users по ключу user_id """
        fact_create_and_num_users = False
        admin = True if update.from_user.id in set(tuple(map(
            int, ADMINS)) if ADMINS else tuple() + tuple(map(
                int, TECH_ADMINS)) if TECH_ADMINS else tuple()) else False

        with self.point_db_connection:
            user, fact_create = self.tables.users.get_or_create(user_id=update.from_user.id)
            if fact_create:
                fact_create_and_num_users = self.tables.users.select().count()
                user.user_id = int(update.from_user.id)
                user.username = update.from_user.username
                user.first_name = update.from_user.first_name
                user.last_name = update.from_user.last_name
                user.position = "admin" if admin else "user"
                user.password = "admin" if admin else None
                user.save()

        text = 'created new user' if fact_create else 'get user'
        if settings.DEBUG:
            self.logger.debug(self.sign + f' {text.upper()}: {user.username=} | {user.user_id=}')
        return user, fact_create_and_num_users

    async def get_all_users(self, id_only: bool = False, not_ban: bool = False) -> Tuple:
        if not_ban and id_only:
            result = tuple(self.tables.users.select(
                self.tables.users.user_id).where(self.tables.users.ban_from_user == 0))
            if settings.DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users_id WHERE '
                                              f'ban != ban num: {len(result) if result else None}')

        elif id_only:
            result = tuple(self.tables.users.select(self.tables.users.user_id))
            if settings.DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users_id '
                                              f'num: {len(result) if result else None}')

        else:
            result = self.tables.users.select()
            if settings.DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users fields '
                                              f'num: {len(result) if result else None}')

        return result

    async def update_user_balance(
            self, user_id: str, up_balance: Optional[str] = None,
            down_balance: Optional[str] = None, zero_balance: bool = False) -> Union[Tuple, bool]:
        user = self.tables.users.get_or_none(user_id=user_id)
        if not user:
            return False

        if up_balance and up_balance.isdigit():
            user.balance += int(up_balance)
        elif down_balance and down_balance.isdigit():
            user.balance -= int(down_balance)
        elif zero_balance:
            user.balance = 0
        else:
            return False, 'bad data'
        user.save()

        if up_balance:
            result = f'up_balance: {up_balance}'
        elif down_balance:
            result = f'down_balance: {down_balance}'
        else:
            result = f'zero_balance: {zero_balance}'
        if settings.DEBUG:
            self.logger.debug(self.sign + f'{user_id=} | {result=} | new {user.balance=}')
        return True, user.balance, user.username

    async def update_user_balance_requests(self, user_id: Union[str, int],
                                           up_balance: Optional[Union[str, int]] = None,
                                           down_balance: Optional[Union[str, int]] = None,
                                           zero_balance: bool = False) -> Union[Tuple, bool]:
        user = self.tables.users.get_or_none(user_id=str(user_id))
        if not user:
            return False

        if up_balance and str(up_balance).isdigit():
            user.balance_requests += int(up_balance)
        elif down_balance and str(down_balance).isdigit():
            if user.balance_requests != 0:
                user.balance_requests -= int(down_balance)
            else:
                return False, 'not update user balance_requests=0'
        elif zero_balance:
            user.balance_requests = 0
        else:
            return False, 'bad data'
        user.save()

        if up_balance:
            result = f'up_balance: {up_balance}'
        elif down_balance:
            result = f'down_balance: {down_balance}'
        else:
            result = f'zero_balance: {zero_balance}'
        if settings.DEBUG:
            self.logger.debug(self.sign + f'{user_id=} | {result=} | new {user.balance_requests=}')
        return True, user.balance_requests, user.username

    async def update_user_access(
            self, user_id: Union[str, int], block: bool = False) -> Union[bool, Tuple]:
        user = self.tables.users.get_or_none(user_id=user_id)
        if not user:
            return False
        if block:
            user.access = 'block'
        else:
            user.access = 'allowed'
        user.save()
        if settings.DEBUG:
            self.logger.debug(self.sign + f'func update_user_access -> '
                                          f'{"BLOCK" if block else "ALLOWED"} '
                                          f'| user_id: {user_id}')
        return True, user.username

    async def update_ban_from_user(
            self, update, ban_from_user: bool = False) -> Union[bool, tuple]:
        user: Tables.users = self.tables.users.get_or_none(user_id=update.from_user.id)
        if not user:
            return False
        user.ban_from_user = ban_from_user
        user.save()
        if settings.DEBUG:
            self.logger.debug(self.sign + f'func update_ban_from_user -> user: {user.username} | '
                                          f'user_id: {update.from_user.id} | ban: {ban_from_user}')
        return True, user.username

    async def count_users(
            self,
            all_users: bool = False,
            register: bool = False,
            date: Optional[datetime] = None) -> str:
        if all_users:
            nums = self.tables.users.select().count()
            if settings.DEBUG:
                self.logger.debug(self.sign + f'func count_users -> all users {nums}')

        elif register:
            nums = self.tables.users.select().wheere(self.tables.users.date_join == date).count()
            if settings.DEBUG:
                self.logger.debug(self.sign + 'func count_users -> num users: '
                                              f'{nums} WHERE date_join == date: {date}')

        else:
            nums = self.tables.users.select().where(
                self.tables.users.date_last_request >= date).count()
            if settings.DEBUG:
                self.logger.debug(self.sign + f'func count_users -> num users: {nums} '
                                              f'WHERE date_last_request == date: {date}')

        return nums

    async def select_all_contacts_users(self) -> Tuple:
        users = self.tables.users.select(
            self.tables.users.user_id,
            self.tables.users.first_name,
            self.tables.users.username,
            self.tables.users.date_join,
            self.tables.users.date_last_request,
            self.tables.users.text_last_request,
            self.tables.users.num_requests,
            self.tables.users.ban_from_user)

        if not users:
            if settings.DEBUG:
                self.logger.error(self.sign + 'BAD -> NOT users in DB')
        else:
            if settings.DEBUG:
                self.logger.debug(self.sign + 'OK -> SELECT all contacts users -> '
                                              f'return -> {len(users)} users contacts')

        return users

    async def select_password(self, user_id: int) -> str:
        user = self.tables.users.select(
            self.tables.users.password).where(self.tables.users.user_id == user_id).get()
        if settings.DEBUG:
            self.logger.debug(self.sign + 'func select_password password -> '
                                          f'len password {len(user.password)}')

        return user.password

    async def update_last_request_data(self, update, text_last_request: str) -> Optional[bool]:
        user = self.tables.users.get_or_none(user_id=update.from_user.id)
        if not user:
            return False

        user.date_last_request = datetime.now()
        user.num_requests += 1
        user.text_last_request = text_last_request
        user.save()
        if settings.DEBUG:
            self.logger.debug(self.sign + 'func update_last_request_data -> '
                                          f'user: {update.from_user.username} | '
                                          f'user_id:{update.from_user.id} | '
                                          f'last_request_data: {text_last_request}')

    """ Методы работы с таблицей payments"""
    async def create_new_payment_order(self, user_id):
        """Создаёт запись о новой оплате"""
        order_num = self.tables.payments.insert(user_id=user_id).execute()
        if settings.DEBUG:
            self.logger.info(self.sign + f'create new payment_order: {order_num=}')
        return order_num

    async def update_payment_order(self, order_num, payment_link: Optional[str] = None,
                                   payment_link_data: Optional[Dict] = None):
        """Обновляет запись об оплате"""
        if order := self.tables.payments.get_or_none(id=order_num):
            if payment_link:
                order.payment_link = payment_link
            if payment_link_data:
                order.payment_link_data = payment_link_data
            order.save()
            if settings.DEBUG:
                self.logger.info(self.sign + f'update payment_order: '
                                             f'{order.__dict__.get("__data__")}')
            return order

    async def select_all_payment_orders_user(self, user_id):
        """Возвращает все записи об оплатах пользователя"""
        payment_orders_user = list(self.tables.payments.select().where(
            self.tables.payments.user_id == user_id))
        return payment_orders_user
