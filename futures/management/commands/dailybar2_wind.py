import os
import numpy as np
import pandas as pd
from WindPy import w
from sqlalchemy import create_engine
from django.core.management.base import BaseCommand

from futures import models


def _sanitize_symbol(contract):
    symbol = contract.symbol_temp or contract.symbol
    exchange = contract.root_symbol.exchange.symbol
    return f'{symbol}.{exchange}'.upper()


def _convert_nan(val, default=None):
    if np.isnan(val):
        return default
    return val


ENGINE = create_engine(
    'mysql+pymysql://rm-2zedo2m914a92z7rhfo.mysql.rds.aliyuncs.com',
    connect_args={'read_default_file': os.path.expanduser('~/my.cnf')},
)


class Command(BaseCommand):
    help = """
    fill the missing day's pricing data
    Usage: python manage.py dailybar2_wind AL 20081208
    """

    def add_arguments(self, parser):
        parser.add_argument('rs', type=str, help='root symbol')
        parser.add_argument('dt', type=str, help='datetime')
        parser.add_argument('--s', type=str, help='contract symbol')

    def handle(self, *args, **kwargs):
        w.start()

        dt = pd.Timestamp(kwargs['dt'])
        if kwargs['s']:
            contracts = models.Contract.objects.filter(symbol=kwargs['s'])
        else:
            contracts = models.Contract.objects.filter(
                root_symbol__symbol=kwargs['rs'],
                contract_issued__lte=dt,
                last_traded__gte=dt,
            )

        for contract in contracts:
            fields = ['open', 'high', 'low', 'close', 'volume', 'oi']
            response = w.wsd(
                _sanitize_symbol(contract), ','.join(fields), dt, dt)

            if response.ErrorCode == -40522017:
                raise Exception('Reach data limit!')
            elif response.ErrorCode == -40520007:
                continue  # no data

            dt = pd.Timestamp(response.Times[0])
            _, created = models.DailyBar.objects.update_or_create(
                contract=contract,
                datetime=dt,
                defaults={'open': _convert_nan(response.Data[0][0]),
                          'high': _convert_nan(response.Data[1][0]),
                          'low': _convert_nan(response.Data[2][0]),
                          'close': _convert_nan(response.Data[3][0]),
                          'volume': _convert_nan(response.Data[4][0], 0),
                          'open_interest': _convert_nan(response.Data[5][0], 0)}
            )

            if created:
                self.stdout.write(f"{contract}({dt}), created")
            else:
                self.stdout.write(f"{contract}({dt}), updated")

        w.close()
