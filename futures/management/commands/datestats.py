from django.db.models import Max, Min
from django.core.management.base import BaseCommand

from futures import models


class Command(BaseCommand):
    help = """
    Return max date from daily bar model.
    Usage:
        python manage.py date_stats
        python manage.py date_stats --by=IF2006
        python manage.py date_stats --table=minute
    """

    def add_arguments(self, parser):
        parser.add_argument('--by', type=str, help='max and min date by')
        parser.add_argument('--table', type=str, help='minute or daily')

    def handle(self, *args, **kwargs):
        by_ = kwargs['by'] or 'exchange'
        m = models.MinuteBar \
            if kwargs['table'] and kwargs['table'].startswith('m') \
            else models.DailyBar

        if by_ == 'exchange':
            dates = m.objects.values(
                'contract__root_symbol__exchange__symbol'
            ).annotate(
                min_date=Min('datetime'),
                max_date=Max('datetime')
            )
            for date in dates:
                print(date)
        else:
            self.stdout.write(
                f'{by_}: '
                f'{m.objects.filter(contract__symbol=by_).earliest().datetime}'
                ' ~ '
                f'{m.objects.filter(contract__symbol=by_).latest().datetime}'
            )
