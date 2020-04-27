import numpy as np
import pandas as pd
from tqsdk import TqApi
from django.core.management.base import BaseCommand

from futures import models


def _convert_nan(val, default=None):
    if np.isnan(val):
        return default
    return val


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
            df = api.get_kline_serial(_sanitize_symbol(contract), 60, 8964)
            df['datetime'] = pd.to_datetime(df['datetime'])

            df.sort_values(by=['datetime'], ascending=False, inplace=True)

            for _, row in df.iterrows():
                _, created = models.MinuteBar.objects.get_or_create(
                    contract=contract,
                    datetime=row['datetime'],
                    defaults={
                        'open': _convert_nan(row['open']),
                        'high': _convert_nan(row['high']),
                        'low': _convert_nan(row['low']),
                        'close': _convert_nan(row['close']),
                        'volume': _convert_nan(row['volume'], 0),
                        'open_interest': _convert_nan(row['close_oi'], 0),
                    }
                )

                if created:
                    self.stdout.write(f"{contract.id}({row['datetime']}), created")
                else:
                    # since we are looping from latest to oldest bars
                    # if we met the first datetime which exists in the database
                    # break the inserting process
                    break

        api.close()
