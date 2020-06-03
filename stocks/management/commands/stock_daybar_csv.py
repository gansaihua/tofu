import pandas as pd
from aldjemy.core import get_engine
from django.core.management.base import BaseCommand

from stocks import models

# _DEF_FOLDER = 'stocks/management/fixtures/'
_DEF_FOLDER = 'D:/tmp/'

# We write into the intermediary table
# which will be batch inserted into the target table
# will ignore existed bar rather update it
TABLE_NAME = 'stocks_daybar_changes'

COLUMNS = {
    '日期': 'datetime',
    '开盘价(元)': 'open',
    '最高价(元)': 'high',
    '最低价(元)': 'low',
    '收盘价(元)': 'close',
    '成交量(股)': 'volume',
    '成交金额(元)': 'amount',
}
OHLC = ['open', 'high', 'low', 'close']
VA = ['volume', 'amount']


class Command(BaseCommand):
    help = """
    fill the previous stocks' pricing data
    Usage: python manage.py stock_daybar_csv --s=000001.SH
    """

    def add_arguments(self, parser):
        parser.add_argument('--s', type=str, help='wind code')

    def handle(self, *args, **kwargs):
        if kwargs['s']:
            codes = models.Code.objects.filter(wind_code=kwargs['s'])
        else:
            codes = models.Code.objects.all()  # .filter(active=True)

        for code in codes:
            file_name = _DEF_FOLDER + code.wind_code.upper() + '.csv'
            try:
                df = pd.read_csv(file_name, parse_dates=['日期'], encoding='gbk')
            except FileNotFoundError:
                continue

            df.rename(columns=COLUMNS, inplace=True)
            df = df[COLUMNS.values()]
            df[OHLC] = df[OHLC].fillna(method='ffill')
            df[VA] = df[VA].fillna(0)
            df.dropna(subset=OHLC, how='all', inplace=True)

            dt = df['datetime'].dt.tz_localize('Asia/Shanghai').values
            df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

            df['code_id'] = code.id

            df.to_sql(TABLE_NAME,
                      get_engine(),
                      if_exists='append',
                      index=False,
                      method='multi')

            self.stdout.write(f"{code}({code.id}): {len(df)}")
