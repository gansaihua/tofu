import numpy as np
import pandas as pd
from futures import models
from django.core.management.base import BaseCommand


_DEF_FOLDER = 'futures/management/fixtures/'
_DEF_FILE = 'contracts_issued.xlsx'


class Command(BaseCommand):
    help = """
    Import futures meta information (in excel format) to database.
    created by
    Wind -> 数据集 -> 期货 -> 期货合约列表

    Usage:
        python manage.py contracts_issued --f=contracts_issued.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('--f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures contract issued date')

        file_name = _DEF_FOLDER + (kwargs['f'] or _DEF_FILE)
        df = pd.read_excel(file_name,
                           parse_dates=['contract_issued'])

        for _, row in df.iterrows():
            if np.isnan(row['id']):
                contract = models.Contract.objects.get(
                    symbol=row['symbol'],
                    root_symbol__exchange__symbol=row['exchange'])
            else:
                contract = models.Contract.objects.get(pk=row['id'])

            contract.contract_issued = row['contract_issued']
            contract.save()
            self.stdout.write(f"{contract}, updated")
