import django

import os
import sys

_d = os.path.dirname

django_setting_path = _d(_d(__file__))
sys.path.append(django_setting_path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'tofu.settings',
)

django.setup()

from django.db import connection
from futures.models import Exchange, RootSymbol, Contract, DailyBar as FuturesDayBar
from stocks.models import Code, DayBar as StockDayBar
