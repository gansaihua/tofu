import re
import numpy as np
import pandas as pd
from futures import models
from django.core.management.base import BaseCommand


DEFAULT_FILE = 'futures/management/fixtures/futures_code.xlsx'


class Command(BaseCommand):
    help = """
    Import futures meta information (in excel format) to database.
    created by
    Wind -> 数据集 -> 期货 -> 期货合约列表

    Usage:
        python manage.py update_futures_code --f=../fixtures/futures_code.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('--f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures code')

        file_name = kwargs['f'] or DEFAULT_FILE
        df = pd.read_excel(file_name, skiprows=range(5))

        for _, row in df.iterrows():
            symbol, exchange = row['wind代码'].split('.')

            exchange = models.Exchange.objects.get(symbol=exchange)

            root_symbol = re.match(r'^(\w{1,2}?)\d{4}$', symbol).group(1)
            root_symbol = models.ContinuousFutures.objects.get(
                symbol=root_symbol,
                exchange=exchange,
            )

            margin = row['交易保证金']
            if np.isnan(margin):
                margin = None

            day_limit = row['涨跌幅限制']
            if np.isnan(day_limit):
                day_limit = None

            contract_issued = row['合约上市日']
            last_traded = row['最后交易日']
            delivery = row['最后交割日']
            code, created = models.Code.objects.update_or_create(
                root_symbol=root_symbol,
                symbol=symbol,
                defaults={
                    'margin': margin,
                    'day_limit': day_limit,
                    'contract_issued': contract_issued,
                    'last_traded': last_traded,
                    'delivery': delivery,
                },
            )

            if created:
                code.name = row['名称']
                code.save()

                self.stdout.write(f"{code}, created")
            else:
                self.stdout.write(f"{code}, updated")