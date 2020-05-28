import os
import pandas as pd
from sqlalchemy import create_engine
from django.core.management.base import BaseCommand

from futures import models


# We write into the intermediary table
# which will batch insert into the target table `futures_minutebar`
TABLE_NAME = 'futures_minutebar_changes'
USED_COLUMNS = ['contract_id', 'datetime', 'open',
                'high', 'low', 'close', 'volume', 'open_interest']
ENGINE = create_engine(
    'mysql+pymysql://rm-2zedo2m914a92z7rhfo.mysql.rds.aliyuncs.com',
    connect_args={'read_default_file': os.path.expanduser('~/my.cnf')},
)
_DEF_FOLDER = 'futures/management/fixtures/'


class Command(BaseCommand):
    help = """
    Import minute bar data of futures from tqsdk to database.
    with columns (cid, datetime, open, high, low, close, volume, open_interest)

    Wind 终端操作: F5 -> 1分 -> 工具 -> 导出数据 -> 导出原始行情数据
    Usage:
        python manage.py wind_minutebar
    """

    def add_arguments(self, parser):
        parser.add_argument('s', type=str, help='contract symbol')
        parser.add_argument(
            '--f', type=str, help='target file name, default is <symbol>_1m.xlsx'
        )

    def handle(self, *args, **kwargs):
        contract = models.Contract.objects.get(symbol=kwargs['s'])

        file_name = kwargs['f'] or kwargs['s'] + '_1m.xlsx'
        df = pd.read_excel(_DEF_FOLDER + file_name, skip_footer=2)

        df.rename(columns={'日期': 'datetime',
                           '开盘价(元)': 'open',
                           '最高价(元)': 'high',
                           '最低价(元)': 'low',
                           '收盘价(元)': 'close',
                           '成交量(股)': 'volume',
                           '成交量': 'volume',
                           '持仓量': 'open_interest'},
                  inplace=True)

        dt = df['datetime'].dt.tz_localize('Asia/Shanghai').values
        df['datetime'] = dt.astype('datetime64[ns]').astype('int64')

        df['contract_id'] = contract.id

        if 'open_interest' not in df:
            USED_COLUMNS.remove('open_interest')

        df[USED_COLUMNS].to_sql(
            TABLE_NAME, ENGINE, if_exists='append', index=False, method='multi'
        )
        self.stdout.write(f"{contract}: insert {len(df)} rows")
