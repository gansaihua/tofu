import re
from WindPy import w
from django.core.management.base import BaseCommand

from futures import models


class Command(BaseCommand):
    help = """
    Import futures meta information (directly from wind) to database.
    Usage:
        python manage.py update_contracts --f=futures_code.xlsx
    """

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating futures code')

        w.start()

        fields = [
            'margin',
            'mfprice',
            'contractmultiplier',
            'changelt',
            'lasttrade_date',
            'lastdelivery_date',
            'contract_issuedate',
        ]

        contracts = models.Contract.objects.filter(tick_size__isnull=True)
        for contract in contracts:
            symbol = contract.symbol_temp or contract.symbol
            exchange = contract.root_symbol.exchange.symbol

            res = w.wss(f'{symbol}.{exchange}', ','.join(fields))

            if res.ErrorCode == 0 and res.Data[1][0] is not None:
                contract.margin = res.Data[0][0]

                m = re.match(r'^(\d+\.?\d*)(\D*)', res.Data[1][0])

                if m is None:
                    w.close()
                    raise Exception(f'cannot parse tick size for {contract}')

                contract.tick_size = m.group(1)

                contract.multiplier = res.Data[2][0]
                contract.day_limit = res.Data[3][0]
                contract.last_traded = res.Data[4][0]
                contract.delivery = res.Data[5][0]
                contract.save()

                self.stdout.write(f"{contract}, updated")

        w.close()
