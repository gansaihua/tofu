import pandas as pd
from stocks import models
from django.core.management.base import BaseCommand


_DEF_FOLDER = 'stocks/management/fixtures/'
_DEF_FILE = 'stock_code.xlsx'


def sanitize_symbol(symbol, asset):
    if asset in [0, 1]:  # stock or stock index
        return '{:0>6}'.format(str(symbol).strip())
    else:
        return symbol


class Command(BaseCommand):
    help = """
    Usage:
        python manage.py stock_code --f=stock_code.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('--f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating StockCode model')

        file_name = _DEF_FOLDER + (kwargs['f'] or _DEF_FILE)

        df = pd.read_excel(file_name, parse_dates=['start_date', 'end_date'])
        for _, row in df.iterrows():
            code, created = models.Code.objects.update_or_create(
                symbol=sanitize_symbol(row['symbol'], row['asset']),
                exchange=models.Exchange.objects.get(symbol=row['exchange']),
                defaults={
                    'name': row['name'],
                    'asset': row['asset'],
                    'start_date': row['start_date'],
                    'end_date': None if pd.isna(row['end_date']) else row['end_date'],
                }
            )
            if created:
                self.stdout.write(f"{code}, created")
            else:
                self.stdout.write(f"{code}, udpated")
