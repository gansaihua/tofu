import numpy as np
import pandas as pd
from futures import models
from django.core.management.base import BaseCommand


_DEF_FOLDER = 'futures/management/fixtures/'


def _convert_nan(val, default=None):
    if np.isnan(val):
        return default
    return val


class Command(BaseCommand):
    help = """
    Import missing daily bar data of futures (in excel format) to database.
    with columns (cid, datetime, open, high, low, close, volume, open_interest)

    Usage:
        python manage.py update_dailybar_ts FU1901.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures dailybar')

        file_name = _DEF_FOLDER + kwargs['f']
        df = pd.read_excel(file_name)

        for _, row in df.iterrows():
            code = models.Contract.objects.get(pk=row['cid'])
            dt = row['datetime']
            _, created = models.DailyBar.objects.update_or_create(
                contract=code,
                datetime=dt,
                defaults={
                    'open': _convert_nan(row['open']),
                    'high': _convert_nan(row['high']),
                    'low': _convert_nan(row['low']),
                    'close': _convert_nan(row['close']),
                    'volume': _convert_nan(row['volume'], 0),
                    'open_interest': _convert_nan(row['open_interest'], 0),
                }
            )

            if created:
                self.stdout.write(f"{code}({dt}), created")
            else:
                self.stdout.write(f"{code}({dt}), updated")
