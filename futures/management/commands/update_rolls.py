from futures import models, roll_finder
from django.db.models import Max
from django.core.management.base import BaseCommand

DEFALUT_VER = 0


class Command(BaseCommand):
    help = """
    Import futures roll dates to database.
    Usage:
        python manage.py update_rolls --v=2
    """

    def add_arguments(self, parser):
        parser.add_argument('s', type=str)
        parser.add_argument('--v', type=int)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures roll dates')

        ver = kwargs['v'] or DEFALUT_VER

        symbol, exchange = kwargs['s'].upper().split('.')
        root_symbol = models.RootSymbol.objects.get(
            symbol=symbol,
            exchange__symbol=exchange,
        )

        start_date = models.Roll.objects.filter(
            root_symbol=root_symbol,
            verion=ver,
        ).aggregate(Max('datetime'))['datetime__max']

        rolls = roll_finder.get_rolls(root_symbol, start_date)
        for dt, code_id in rolls.iteritems():
            contract = models.Contract.objects.get(pk=code_id)

            print(dt, contract)

            models.Roll.objects.update_or_create(
                verion=ver,
                root_symbol=root_symbol,
                datetime=dt,
                defaults={'contract': contract}
            )
