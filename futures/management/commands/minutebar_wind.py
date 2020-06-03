import pandas as pd
from WindPy import w
from aldjemy.core import get_engine
from django.core.management.base import BaseCommand

from futures import models


def _sanitize_symbol(contract):
    symbol = contract.symbol_temp or contract.symbol
    exchange = contract.root_symbol.exchange.symbol
    return f'{symbol}.{exchange}'.upper()


# We write into the intermediary table
# which will batch insert into the target table `futures_minutebar`
TABLE_NAME = 'futures_minutebar_changes'

OHLC = ['open', 'high', 'low', 'close']
V = ['volume']
OI = ['open_interest']
COLUMNS = OHLC + V + OI + ['contract_id', 'datetime']


class Command(BaseCommand):
    help = """
    Import minute bar data of futures from tqsdk to database.
    with columns (cid, datetime, open, high, low, close, volume, open_interest)

    We use tqsdk for ongoing data updating, and Wind to fill the missing historical bars.
    Here we set the default t1(start) is contract_issued
    and t2(end) is the earliest bar datetime.

    Usage:
        python manage.py wind_minutebar
    """

    def add_arguments(self, parser):
        parser.add_argument('rs', type=str, help='root symbol')
        parser.add_argument('--s', type=str, help='contract symbol')
        parser.add_argument('--t1', type=str, help='start datetime')
        parser.add_argument('--t2', type=str, help='end datetime')

    def handle(self, *args, **kwargs):
        w.start()

        contracts = models.Contract.objects.filter(
            root_symbol__symbol=kwargs['rs']).order_by('-last_traded')
        for contract in contracts:
            if kwargs['s'] and contract.symbol != kwargs['s']:
                continue

            try:
                bar = models.MinuteBar.objects.filter(contract=contract)
                default_end = bar.earliest().datetime
            except models.MinuteBar.DoesNotExist:
                default_end = contract.last_traded

            t1 = kwargs['t1'] or contract.contract_issued
            t2 = kwargs['t2'] or default_end

            fields = ['open', 'high', 'low', 'close', 'volume', 'oi']
            status, df = w.wsi(_sanitize_symbol(contract),
                               ','.join(fields),
                               pd.Timestamp(t1),
                               pd.Timestamp(t2),
                               usedf=True)

            if status == -40522017:
                raise Exception('Reach data limit!')
            elif status != 0 or len(df) == 1:  # or only one bar returned
                continue

            df.rename(columns=str.lower, inplace=True)
            df.rename(columns={'position': 'open_interest'}, inplace=True)

            df[OHLC] = df[OHLC].fillna(method='ffill')
            df[V] = df[V].fillna(0)

            df.dropna(subset=['open', 'high', 'low', 'close'],
                      how='all',
                      inplace=True)

            df.index = pd.to_datetime(df.index)
            dt = df.index.tz_localize('Asia/Shanghai').values
            df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

            df['contract_id'] = contract.id

            df[COLUMNS].to_sql(TABLE_NAME,
                               get_engine(),
                               if_exists='append',
                               index=False,
                               method='multi')

            self.stdout.write(f"{contract}({contract.id}): "
                              f"{t1}, {t2}, {len(df)}")

        w.close()
