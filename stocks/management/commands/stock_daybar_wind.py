import pandas as pd

from WindPy import w
from aldjemy.core import get_engine
from django.core.management.base import BaseCommand

from stocks import models


# We write into the intermediary table
# which will be batch inserted into the target table
# will ignore existed bar rather update it
TABLE_NAME = 'stocks_daybar_changes'

OHLC = ['open', 'high', 'low', 'close']
VA = ['volume', 'amount']


class Command(BaseCommand):
    help = """
    fill the previous contracts' pricing data
    Usage:
    python manage.py stock_daybar --s=000001.SH
    python manage.py stock_daybar --s=000001.SZ
    """

    def add_arguments(self, parser):
        parser.add_argument('--s', type=str, help='wind code')
        parser.add_argument('--t1', type=str, help='start datetime')
        parser.add_argument('--t2', type=str, help='end datetime')

    def handle(self, *args, **kwargs):
        w.start()

        if kwargs['s']:
            codes = models.Code.objects.filter(wind_code=kwargs['s'])
        else:
            codes = models.Code.objects.all()  # .filter(active=True)

        for code in codes:
            try:
                bar = models.DayBar.objects.filter(code=code)
                default_end = bar.earliest().datetime
            except models.DayBar.DoesNotExist:
                default_end = code.end_date or pd.Timestamp('today')

            t1 = kwargs['t1'] or code.start_date
            t2 = kwargs['t2'] or default_end

            fields = ['open', 'high', 'low', 'close', 'volume', 'amt']
            status, df = w.wsd(code.wind_code,
                               ','.join(fields),
                               pd.Timestamp(t1),
                               pd.Timestamp(t2),
                               usedf=True)

            if status == -40522017:
                raise Exception('Reach data limit!')
            elif status != 0 or len(df) == 1:  # only one bar returned
                continue

            df.rename(columns=str.lower, inplace=True)
            df.rename(columns={'amt': 'amount'}, inplace=True)

            df[OHLC] = df[OHLC].fillna(method='ffill')
            df[VA] = df[VA].fillna(0)

            df.dropna(subset=OHLC, how='all',
                      inplace=True)

            df.index = pd.to_datetime(df.index)
            dt = df.index.tz_localize('Asia/Shanghai').values
            df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

            df['code_id'] = code.id

            df.to_sql(TABLE_NAME,
                      get_engine(),
                      if_exists='append',
                      index=False,
                      method='multi')

            self.stdout.write(f"{code}({code.id}): "
                              f"{t1}, {t2}, {len(df)}")

        w.close()
