import pandas as pd

from django.db.models import Max
from django.core.management.base import BaseCommand

from futures import models


_DEF_REF_DATE = pd.Timestamp('today').normalize()


class Command(BaseCommand):
    help = """
    Update the active flag
    Usage:
        python manage.py update_active
    """

    def handle(self, *args, **kwargs):
        contracts = models.Contract.objects.all()
        for contract in contracts:
            if contract.active and contract.last_traded < _DEF_REF_DATE:
                contract.active = False
                contract.save()
                self.stdout.write(f'Deactivate {contract}')
