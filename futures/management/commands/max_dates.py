from django.db.models import Max
from django.core.management.base import BaseCommand

from futures import models


class Command(BaseCommand):
    help = """
    Return max date from daily bar model.
    Usage:
        python manage.py max_dates
    """

    def handle(self, *args, **kwargs):
        dates = models.DailyBar.objects.values(
            'contract__root_symbol__exchange__symbol'
        ).annotate(
            max_date=Max('datetime')
        )

        for date in dates:
            print(date)
