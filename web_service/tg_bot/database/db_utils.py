from typing import Union
from datetime import datetime

from peewee import *
from peewee import ModelBase
from playhouse.sqlite_ext import JSONField, SqliteDatabase

from tg_bot.config import DATABASE_CONFIG, DEFAULT_FREE_BALANCE_REQUEST_USER

databases = {
    'sqlite': SqliteDatabase,
    'postgres': PostgresqlDatabase,
    'mysql': MySQLDatabase
}

db: Union[SqliteDatabase, PostgresqlDatabase, MySQLDatabase] = databases[DATABASE_CONFIG[0]](
    **DATABASE_CONFIG[1]
)


class TelegramUsers(Model):
    """Таблица пользователей телеграм бота"""
    user_id = IntegerField(primary_key=True, unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    referer_id = IntegerField(null=True)  # Телеграм id пользователя по чьей ссылке пришел этот пользователь
    date_join = DateTimeField(default=datetime.now(), null=False)  # Два поля для одного и того-же

    access = CharField(default='allowed', null=False)  # Режим доступа к боту
    start_time_limited = IntegerField(null=True)  # Время начала блокировки пользователя используется в middleware
    position = CharField(null=False, default='user')  # Позиция - user | admin
    password = CharField(null=True)  # Пароль обязателен для admin

    date_last_request = DateTimeField(default=datetime.now(), null=False)  # Дата последнего запроса
    text_last_request = CharField(null=False, default='first start command')  # Текст последнего запроса
    num_requests = IntegerField(null=False, default=1)  # Общее кол-во запросов
    ban_from_user = BooleanField(null=False, default=False)  # Забанил ли пользователь бота

    balance_requests = IntegerField(null=False, default=DEFAULT_FREE_BALANCE_REQUEST_USER)  # Баланс кол-ва запросов разрешенных
    balance = DecimalField(max_digits=10, decimal_places=2, default=0, null=False)  # Финансовый баланс
    subscription = DateTimeField(null=True)  # Подписка до этой даты

    class Meta:
        database = db
        order_by = 'date_join'
        db_table = 'telegram_bot_users'


class TelegramPayment(Model):
    """Таблица платежей пользователей телеграм бота"""
    payment_status = CharField(default='not paid', null=False)
    user_id = ForeignKeyField(TelegramUsers, to_field='user_id', related_name='payments', on_delete='CASCADE')
    payment_link = CharField(null=True)
    payment_link_data = JSONField(null=False, default=dict())
    notification_data = JSONField(null=False, default=dict())
    payment_system = CharField(default='PRODAMUS', null=False)
    order_id_payment_system = CharField(null=True)

    class Meta:
        database = db
        order_by = 'user_id'
        db_table = 'telegram_bot_payments'


class Tables:
    users = TelegramUsers
    payments = TelegramPayment

    @classmethod
    def all_tables(cls):
        return [value for value in cls.__dict__.values() if isinstance(value, ModelBase)]
