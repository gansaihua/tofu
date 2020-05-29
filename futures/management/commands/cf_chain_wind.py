import os
import re
import datetime
import pandas as pd
from WindPy import w
from sqlalchemy import create_engine
from django.core.management.base import BaseCommand

from futures import models

ENGINE = create_engine(
    'mysql+pymysql://rm-2zedo2m914a92z7rhfo.mysql.rds.aliyuncs.com',
    connect_args={'read_default_file': os.path.expanduser('~/my.cnf')},
)


def _f(wind_ticker, root_symbol):
    symbol, e = wind_ticker.split('.')
    assert e.upper() == root_symbol.exchange.symbol, 'Exchange mismatch.'

    m = re.match(r'^(\w{1,2}?)\d{4}$', symbol)
    if m:
        ret = models.Contract.objects.get(symbol=symbol)
    else:
        ret = models.Contract.objects.get(symbol_temp=symbol)
    return ret


class Command(BaseCommand):
    help = """
        python manage.py cf_chain_wind --rs=IF
    """

    def add_arguments(self, parser):
        parser.add_argument('--rs', type=str, help='root symbol')
        parser.add_argument('--t1', type=str, help='start datetime')
        parser.add_argument('--t2', type=str, help='end datetime')
        parser.add_argument('--ver', type=str, default=1, help='version')

    def handle(self, *args, **kwargs):
        w.start()

        if kwargs['rs']:
            rss = models.RootSymbol.objects.filter(symbol=kwargs['rs'])
        else:
            rss = models.RootSymbol.objects.filter(active=True)

        for rs in rss:
            try:
                row = models.ContinuousFutures.objects.filter(
                    root_symbol=rs)
                default_start = row.latest().datetime
            except models.ContinuousFutures.DoesNotExist:
                default_start = rs.launched

            ticker = rs.symbol + '.' + rs.exchange.symbol

            t1 = kwargs['t1'] or default_start
            t2 = kwargs['t2'] or ""

            status, df = w.wsd(
                ticker, 'trade_hiscode',
                t1, t2,
                "Days=Alldays;Fill=Previous",
                usedf=True,
            )

            if status == -40522017:
                raise Exception('Reach data limit!')
            elif status != 0 or len(df) == 1:  # or only one bar returned
                continue

            df.drop_duplicates(inplace=True)

            df.columns = ['contract']
            df['contract'] = df['contract'].apply(lambda x: _f(x, rs))

            for dt, row in df.iterrows():
                cf, created = models.ContinuousFutures.objects.update_or_create(
                    root_symbol=rs,
                    datetime=dt,
                    contract=row['contract'],
                    version=kwargs['ver']
                )

                if created:
                    self.stdout.write(f"{rs}({dt}): created - v{kwargs['ver']}")
                else:
                    self.stdout.write(f"{rs}({dt}): updated - v{kwargs['ver']}")

        w.close()
