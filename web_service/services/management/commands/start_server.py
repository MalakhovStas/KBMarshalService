# from django.core.management.base import BaseCommand, CommandError
#
#
# class Command(BaseCommand):
#     help = "Closes the specified poll for voting"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     # def add_arguments(self, parser):
#     #     parser.add_argument("poll_ids", nargs="+", type=int)
#
#     def handle(self, *args, **options):
#         # for poll_id in options["poll_ids"]:
#         #     try:
#         #         poll = Poll.objects.get(pk=poll_id)
#         #     except Poll.DoesNotExist:
#         #         raise CommandError('Poll "%s" does not exist' % poll_id)
#         #
#         #     poll.opened = False
#         #     poll.save()
#
#         self.stdout.write(self.style.SUCCESS('Successfully Hello World!!!'))


#=------------------------------------------------------------------------------------------

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.commands.runserver import Command as RunserverCommand
from services import loader


class Command(RunserverCommand):
    help = (
        "Starts a lightweight web server for development and also serves static files."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--nostatic",
            action="store_false",
            dest="use_static_handler",
            help="Tells Django to NOT automatically serve static files at STATIC_URL.",
        )
        parser.add_argument(
            "--insecure",
            action="store_true",
            dest="insecure_serving",
            help="Allows serving static files even if DEBUG is False.",
        )

    def get_handler(self, *args, **options):
        """
        Return the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise return the default handler.
        """
        loader.logger.debug("START loader")
        handler = super().get_handler(*args, **options)
        use_static_handler = options["use_static_handler"]
        insecure_serving = options["insecure_serving"]
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return StaticFilesHandler(handler)
        return handler

#=======================================================================================

# from django.contrib.staticfiles.management.commands.runserver import Command
#
# class Command(Command):
#     def get_handler(self, *args, **kwargs):
#         from services import loader
#         loader.logger.debug("START loader")
#         # self.stdout.write(self.style.SUCCESS('Successfully Hello World!!!'))
#         super().get_handler(self, *args, **kwargs)
