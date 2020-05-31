import os
import pandas as pd
from WindPy import w
from sqlalchemy import create_engine
from django.core.management.base import BaseCommand

from futures import models


def _sanitize_symbol(contract):
    symbol = contract.symbol_temp or contract.symbol
    exchange = contract.root_symbol.exchange.symbol
    return f'{symbol}.{exchange}'.upper()


# We write into the intermediary table
# which will be batch inserted into the target table
# will ignore existed bar rather update it
TABLE_NAME = 'futures_dailybar_changes'

OHLC = ['open', 'high', 'low', 'close', 'volume']
V = ['volume']
OI = ['open_interest']
COLUMNS = OHLC + V + OI + ['contract_id', 'datetime']

ENGINE = create_engine(
    'mysql+pymysql://rm-2zedo2m914a92z7rhfo.mysql.rds.aliyuncs.com',
    connect_args={'read_default_file': os.path.expanduser('~/my.cnf')},
)


class Command(BaseCommand):
    help = """
    fill the previous contracts' pricing data
    Usage: python manage.py dailybar_wind IF
    """

    def add_arguments(self, parser):
        parser.add_argument('rs', type=str, help='root symbol')
        parser.add_argument('--s', type=str, help='contract symbol')
        parser.add_argument('--t1', type=str, help='start datetime')
        parser.add_argument('--t2', type=str, help='end datetime')

    def handle(self, *args, **kwargs):
        w.start()

        if kwargs['s']:
            contracts = models.Contract.objects.filter(symbol=kwargs['s'])
        else:
            contracts = models.Contract.objects.filter(
                root_symbol__symbol=kwargs['rs']).order_by('-last_traded')

        for contract in contracts:
            try:
                bar = models.DailyBar.objects.filter(contract=contract)
                default_end = bar.earliest().datetime
            except models.DailyBar.DoesNotExist:
                default_end = contract.last_traded

            t1 = kwargs['t1'] or contract.contract_issued
            t2 = kwargs['t2'] or default_end

            fields = ['open', 'high', 'low', 'close', 'volume', 'oi']
            status, df = w.wsd(_sanitize_symbol(contract),
                               ','.join(fields),
                               pd.Timestamp(t1),
                               pd.Timestamp(t2),
                               usedf=True)

            if status == -40522017:
                raise Exception('Reach data limit!')
            elif status != 0 or len(df) == 1:  # or only one bar returned
                continue

            df.rename(columns=str.lower, inplace=True)
            df.rename(columns={'oi': 'open_interest'}, inplace=True)

            df[OHLC] = df[OHLC].fillna(method='ffill')
            df[V] = df[V].fillna(0)

            df.dropna(subset=OHLC, how='all',
                      inplace=True)

            df.index = pd.to_datetime(df.index)
            dt = df.index.tz_localize('Asia/Shanghai').values
            df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

            df['contract_id'] = contract.id

            df[COLUMNS].to_sql(TABLE_NAME,
                               ENGINE,
                               if_exists='append',
                               index=False,
                               method='multi')

            self.stdout.write(f"{contract}({contract.id}): "
                              f"{t1}, {t2}, {len(df)}")

        w.close()
