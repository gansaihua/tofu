import re
import numpy as np
import pandas as pd
from futures import models
from django.core.management.base import BaseCommand


_DEF_FOLDER = 'futures/management/fixtures/'
_DEF_MIN_DATES = {
    'DCE': pd.Timestamp('2006-01-04'),
    'CFE': pd.Timestamp('2010-04-16'),
    'INE': pd.Timestamp('2018-03-26'),
    'SHF': pd.Timestamp('2002-12-02'),
    'CZC': pd.Timestamp('2005-05-09'),
}


def _sanitize_code(raw_code, dt):
    """
    raw_code: 'FG911', 'LR007'
    return: 'FG1911', 'LR2007'
    """
    dt = min(pd.Timestamp(dt), pd.Timestamp('today'))

    ref = dt.strftime('%y%m')
    calendar = ref[0] + raw_code[2:]
    if int(calendar) < int(ref):
        calendar = str(int(calendar) + 1000)

    symbol = raw_code[:2]
    return symbol + calendar


def _sanitize_column(column):
    m = re.match(
        r'^(\w+?)\s*\[交易日期\]\s*(\d{4}-\d{2}-\d{2}).*?$',
        column,
        flags=re.DOTALL)

    if m:
        return m.group(1), m.group(2)
    else:
        return column


def _sanitize_columns(columns):
    ret = []
    dt = None
    for column in columns:
        tmp = _sanitize_column(column)
        if len(tmp) == 2:
            ret.append(tmp[0])
            if dt is None:
                dt = tmp[1]
        else:
            ret.append(tmp)
    return ret, dt


def _convert_nan(val, default=None):
    if np.isnan(val):
        return default
    return val


class Command(BaseCommand):
    help = """
    Import missing daily bar data of futures (in excel format) to database.
    created by
    Wind -> 商品 -> 数据浏览器 -> 退市合约 -> 行情指标

    Usage:
        python manage.py update_dailybar shf_20040625.xlsx
    """

    def add_arguments(self, parser):
        parser.add_argument('f', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures dailybar')

        file_name = _DEF_FOLDER + kwargs['f']
        df = pd.read_excel(file_name)
        df.columns, dt = _sanitize_columns(df.columns)

        for _, row in df.iterrows():
            symbol, exchange = row['证券代码'].split('.')

            m = re.match(r'^(\w{1,2}?)\d{4}$', symbol)
            if m:
                root_symbol = m.group(1)
            else:
                symbol = _sanitize_code(symbol, dt)
                root_symbol = re.match(r'^(\w{1,2}?)\d{4}$', symbol).group(1)

            root_symbol = models.RootSymbol.objects.get(
                symbol=root_symbol,
                exchange__symbol=exchange,
            )

            code = models.Contract.objects.get(
                root_symbol=root_symbol,
                symbol=symbol,
            )

            _, created = models.DailyBar.objects.update_or_create(
                contract=code,
                datetime=dt,
                defaults={
                    'open': _convert_nan(row['开盘价']),
                    'high': _convert_nan(row['最高价']),
                    'low': _convert_nan(row['最低价']),
                    'close': _convert_nan(row['收盘价']),
                    'volume': _convert_nan(row['成交量'], 0),
                    'open_interest': _convert_nan(row['持仓量'], 0),
                }
            )

            if created:
                self.stdout.write(f"{code}({dt}), created")
            else:
                self.stdout.write(f"{code}({dt}), updated")
