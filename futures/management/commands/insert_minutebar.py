import re
import numpy as np
import pandas as pd
from tqsdk import TqApi
from django.core.management.base import BaseCommand

from futures import models


# In case symbol are repeated used
# mainly used for CZC
SYMBOL_USED = {
    'CZC': [],
    'SHF': [],
    'INE': [],
    'DCE': [],
    'CFE': [],
}


def _convert_nan(val, default=None):
    if np.isnan(val):
        return default
    return val


def _sanitize_symbol(contract):
    symbol = contract.symbol
    exchange = contract.root_symbol.exchange.symbol

    if exchange == 'CFE':
        ret = f'CFFEX.{symbol.upper()}'
    elif exchange == 'SHF':
        ret = f'SHFE.{symbol.lower()}'
    elif exchange == 'INE':
        ret = f'INE.{symbol.lower()}'
    elif exchange == 'DCE':
        ret = f'DCE.{symbol.lower()}'
    elif exchange == 'CZC':
        m = re.match(r'^(\w{1,2}?)(\d{4})$', symbol)

        if m:
            s, dt = m.groups()
        else:
            raise Exception('Not supported symbol.')

        symbol = s + dt[1:]
        ret = f'CZCE.{symbol.upper()}'
    else:
        raise Exception('Not supported exchange.')

    return ret


class Command(BaseCommand):
    help = """
    Import minute bar data of futures from tqsdk to database.
    with columns (cid, datetime, open, high, low, close, volume, open_interest)

    Usage:
        python manage.py insert_minutebar INE
    """

    def add_arguments(self, parser):
        parser.add_argument('e', type=str, help='exchange name')

    def handle(self, *args, **kwargs):
        self.stdout.write('Insert futures minute bar')

        exchange = kwargs['e'].upper()

        # order by last-traded is necessarily
        # we always want the latest contract
        # to use the symbol first, like `ZC101`
        contracts = models.Contract.objects.filter(
            root_symbol__exchange__symbol=exchange
        ).order_by('-last_traded')

        api = TqApi()
        for contract in contracts:
            tqsdk_symbol = _sanitize_symbol(contract)
            if tqsdk_symbol in SYMBOL_USED[exchange]:
                continue
            else:
                SYMBOL_USED[exchange].append(tqsdk_symbol)

            df = api.get_kline_serial(tqsdk_symbol, 60, 8964)
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
                    # since we are looping from latest to oldest days
                    # if we met the first datetime which exists in the database
                    # break the inserting process
                    break

        api.close()
