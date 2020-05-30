import numpy as np
import pandas as pd
from futures import models
from django.core.management.base import BaseCommand


_DEF_FOLDER = 'futures/management/fixtures/'
_DEF_FILE = 'root_symbols.xlsx'


class Command(BaseCommand):
    help = """
    Usage:
        python manage.py root_symbols --f=root_symbols.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('--f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating rootsymbol table')

        file_name = _DEF_FOLDER + (kwargs['f'] or _DEF_FILE)
        df = pd.read_excel(file_name,
                           parse_dates=['launched'])

        for _, row in df.iterrows():
            if np.isnan(row['id']):
                obj = models.RootSymbol.objects.get(
                    symbol=row['symbol'],
                    exchange__symbol=row['exchange'])
            else:
                obj = models.RootSymbol.objects.get(pk=row['id'])

            obj.launched = row['launched']
            obj.tick_size = row['tick_size']
            obj.margin = row['margin']
            obj.multiplier = row['multiplier']
            obj.commission = row['commission']
            obj.commission_type = row['commission_type']

            obj.save()

            self.stdout.write(f"{obj}, updated")
