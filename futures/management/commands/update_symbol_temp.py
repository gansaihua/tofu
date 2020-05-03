import re
from django.core.management.base import BaseCommand

from futures import models


SYMBOL_TEMP_USED = []


def _get_symbol_temp(symbol):
    m = re.match(r'^(\w{1,2}?)(\d{4})$', symbol)
    if m:
        s, dt = m.groups()
    else:
        raise Exception('Not supported symbol.')
    return s + dt[1:]


class Command(BaseCommand):
    help = """
    Generate and update temp symbol for contracts traded in CZC exchange
    Usage:
        python manage.py generate_symbol_temp
    """

    def handle(self, *args, **kwargs):
        rs = models.RootSymbol.objects.filter(exchange__symbol='CZC')

        for root_symbol in rs:
            contracts = models.Contract.objects.filter(
                root_symbol=root_symbol
            ).order_by('-last_traded')

            for contract in contracts:
                if contract.symbol_temp is not None:
                    contract.symbol_temp = None
                    contract.save()

                    self.stdout.write(f'Remove symbol_temp for {contract}')

                symbol_temp = _get_symbol_temp(contract.symbol)
                if symbol_temp not in SYMBOL_TEMP_USED:
                    contract.symbol_temp = symbol_temp
                    contract.save()

                    SYMBOL_TEMP_USED.append(symbol_temp)

                    self.stdout.write(f'Add symbol_temp for {contract}')
