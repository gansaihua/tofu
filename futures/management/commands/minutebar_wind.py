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
# which will batch insert into the target table `futures_minutebar`
TABLE_NAME = 'futures_minutebar_changes'
USED_COLUMNS = ['contract_id', 'datetime', 'open',
                'high', 'low', 'close', 'volume', 'open_interest']
ENGINE = create_engine(
    'mysql+pymysql://rm-2zedo2m914a92z7rhfo.mysql.rds.aliyuncs.com',
    connect_args={'read_default_file': 'd:/mysql.cnf'},
)


class Command(BaseCommand):
    help = """
    Import minute bar data of futures from tqsdk to database.
    with columns (cid, datetime, open, high, low, close, volume, open_interest)

    Usage:
        python manage.py wind_minutebar2
    """

    def add_arguments(self, parser):
        parser.add_argument('s', type=str, help='contract symbol')
        parser.add_argument('t1', type=str, help='start datetime')
        parser.add_argument('t2', type=str, help='end datetime')

    def handle(self, *args, **kwargs):
        contract = models.Contract.objects.get(symbol=kwargs['s'])

        w.start()

        symbol = _sanitize_symbol(contract)
        t1 = pd.Timestamp(kwargs['t1'])
        t2 = pd.Timestamp(kwargs['t2'])
        fields = ['open', 'high', 'low', 'close', 'volume', 'oi']

        status, df = w.wsi(symbol, ','.join(fields), t1, t2, usedf=True)

        w.close()

        if status != 0:
            raise Exception('Reach data limit!')

        df.rename(columns={'position': 'open_interest'},
                  inplace=True)

        dt = df.index.tz_localize('Asia/Shanghai').values
        df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

        df['contract_id'] = contract.id

        if 'open_interest' not in df:
            USED_COLUMNS.remove('open_interest')

        df[USED_COLUMNS].to_sql(
            TABLE_NAME, ENGINE, if_exists='append', index=False, method='multi'
        )
        self.stdout.write(f"{contract}({contract.id}): insert {len(df)} rows")
