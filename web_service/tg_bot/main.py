import time

from aiogram.types import BotCommand

from . import config
from .loader import logger, bot, dp #, aufm, scheduler
from .utils.admins_send_message import func_admins_message
from django.conf import settings
from . import middlewares


# import logging
# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def start(restart=0) -> None:
    """ Функция запуска приложения с механизмом автоматического перезапуска
        в случае завершения программы в результате непредвиденной ошибки """

    try:
        if settings.DEBUG:
            logger.info('-> START_BOT <-')
        await func_admins_message(message='&#128640 <b>START BOT</b> &#128640')

        await bot.set_my_commands(
            [BotCommand(command=item[0], description=item[1]) for item in config.DEFAULT_COMMANDS])

        await bot.delete_webhook(drop_pending_updates=True)
        # scheduler.start()
        await dp.start_polling(bot)
    except Exception as exc:
        print(exc.__class__)
        if settings.DEBUG:
            logger.critical(f'CRITICAL_ERROR: {exc}')

        await func_admins_message(message=f'&#9762&#9760 <b>BOT CRITICAL ERROR</b> &#9760&#9762'
                                          f'\n<b>File</b>: main.py\n'
                                          f'<b>Exception</b>: {exc.__class__.__name__}\n'
                                          f'<b>Traceback</b>: {exc}', exc=True)

        if config.MAX_RESTART_BOT - restart:
            restart += 1
            await func_admins_message(message=f'&#9888<b>WARNING</b>&#9888\n'
                                              f'<b>10 seconds to {restart} restart BOT</b>!', exc=True)
            if settings.DEBUG:
                logger.warning(f'-> 10seconds to {restart} restart BOT <-')
            time.sleep(10)

            await start(restart=restart)
        else:
            await func_admins_message(message=f'&#9760<b>BOT IS DEAD</b>&#9760')
            if settings.DEBUG:
                logger.critical('-> BOT IS DEAD <-')


# if __name__ == '__main__':
#     asyncio.run(start())
