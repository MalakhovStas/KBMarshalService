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

from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    def get_handler(self, *args, **options):
        from services.business_logic import loader
        # loader.logger.debug("START services loader")
        return super().get_handler(*args, **options)