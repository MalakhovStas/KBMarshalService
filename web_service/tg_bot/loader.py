""" Модуль загрузки основных инструментов приложения """
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from .buttons_and_messages.base_classes import Base
from .config import BOT_TOKEN
from .managers.admins_manager import AdminsManager
from .managers.answer_logic_manager import AnswerLogicManager
from .managers.async_db_manager import DBManager
from .managers.openai_manager import OpenAIManager
from .managers.reload_dump_manager import ReloadDumpManager
from .managers.requests_manager import RequestsManager
from .managers.security_manager import SecurityManager

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from managers.prodamus_manager import ProdamusManager


dbase = DBManager()
security = SecurityManager(dbase=dbase, logger=logger)  # должен быть первым из менеджеров
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
rm = RequestsManager(logger=logger)
adm = AdminsManager(bot=bot, logger=logger, dbase=dbase, rm=rm)
ai = OpenAIManager(dbase=dbase, bot=bot, logger=logger)
rdm = ReloadDumpManager(dbase=dbase, logger=logger)
alm = AnswerLogicManager(ai=ai, bot=bot, logger=logger)

Base.ai, Base.bot = ai, bot

# scheduler = AsyncIOScheduler()
# # start_time_scheduler = datetime.now() + timedelta(seconds=5)
# # scheduler.add_job(aufm.finding_unanswered_feedbacks, trigger='interval',
# #                   next_run_time=start_time_scheduler, seconds=AUFM_INTERVAL_SECONDS)
#
# scheduler.add_job(
#   aufm.finding_unanswered_feedbacks, trigger='interval', seconds=AUFM_INTERVAL_SECONDS)
