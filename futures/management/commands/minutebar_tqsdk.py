from tqsdk import TqApi
from sqlalchemy import create_engine
from django.core.management.base import BaseCommand

from futures import models


def _sanitize_symbol(contract):
    symbol = contract.symbol_temp or contract.symbol
    exchange = contract.root_symbol.exchange.symbol

    if exchange == 'CFE':
        ret = f'CFFEX.{symbol.upper()}'
    elif exchange == 'CZC':
        ret = f'CZCE.{symbol.upper()}'
    elif exchange == 'SHF':
        ret = f'SHFE.{symbol.lower()}'
    elif exchange in ('INE', 'DCE'):
        ret = f'{exchange}.{symbol.lower()}'
    else:
        raise Exception('Not supported exchange.')

    return ret


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
        python manage.py insert_minutebar2
    """

    def add_arguments(self, parser):
        parser.add_argument('--e', type=str, help='exchange name')
        parser.add_argument('--s', type=str, help='contract symbol')
        parser.add_argument('--rs', type=str, help='root symbol')

    def handle(self, *args, **kwargs):
        self.stdout.write('Insert futures minute bar')

        contracts = models.Contract.objects.all()

        symbol = kwargs['s']
        root_symbol = kwargs['rs']
        exchange = kwargs['e']
        if symbol is not None:
            contracts = contracts.filter(symbol__iexact=symbol)
        elif root_symbol is not None:
            contracts = contracts.filter(root_symbol__iexact=root_symbol)
        elif exchange is not None:
            contracts = contracts.filter(
                root_symbol__exchange__symbol__iexact=exchange
            )

        api = TqApi()
        for contract in contracts:
            tq_symbol = _sanitize_symbol(contract)
            df = api.get_kline_serial(tq_symbol, 60, 8964)

            df.rename(columns={'close_oi': 'open_interest'}, inplace=True)
            df['contract_id'] = contract.id

            df[USED_COLUMNS].to_sql(
                TABLE_NAME, ENGINE, if_exists='append', method='multi', index=False
            )
            self.stdout.write(f"{contract.id}: {len(df)}rows")

        api.close()
