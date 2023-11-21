import asyncio

from django.core.management.base import BaseCommand

from tg_bot import main


class Command(BaseCommand):
    help = 'Command for launching a Telegram bot.'

    def handle(self, *args, **kwargs):
        asyncio.run(main.start())
