import re
import pandas as pd
from . import models


def get_primary_contract(root_symbol, dt, exchange=None, offset=5):
    # we need to make sure dt is a trading session
    dt = pd.Timestamp(dt)

    oc = _get_ordered_contracts(root_symbol, exchange)
    front, back = _get_contracts_to_roll(oc, dt)

    front_bars = lookup_bars(front, dt, offset)
    back_bars = lookup_bars(back, dt, offset)

    # If we are within `GRACE_DAYS` of the front contract's auto close
    # date, and a volume flip happened during that period, return the back
    # contract as the active one.
    offset = min(offset, len(back_bars))
    for i in range(1, offset):
        front_vol = front_bars[i].volume
        back_vol = back_bars[i].volume
        if back_vol > front_vol:
            return back
    return front


def lookup_contract(symbol, exchange=None):
    if isinstance(symbol, models.Code):
        return symbol

    if exchange is None:
        symbol, exchange = symbol.split('.')

    assert re.match(r'^\w{1,2}?\d{4}$', symbol) is not None,\
        'Only contract is allowed'

    exchange = models.Exchange.objects.get(
        symbol__iexact=exchange
    )
    symbol = models.Code.objects.get(
        symbol__iexact=symbol, root_symbol__exchange=exchange
    )
    return symbol


def lookup_bars(symbol, dt, offset, exchange=None):
    code = lookup_contract(symbol, exchange)
    qs = models.Bar.objects.filter(
        code=code,
        datetime__lte=dt,
    ).order_by('-datetime')
    return qs[:offset]


def _get_ordered_contracts(root_symbol, exchange=None):
    if exchange is None:
        root_symbol, exchange = root_symbol.split('.')

    assert len(root_symbol) <= 3, 'Only root symbol is allowed'

    exchange = models.Exchange.objects.get(symbol__iexact=exchange)
    root_symbol = models.ContinuousFutures.objects.get(
        symbol__iexact=root_symbol, exchange=exchange
    )
    symbol = models.Code.objects.filter(root_symbol=root_symbol)
    return symbol.order_by('last_traded')


def _get_contracts_to_roll(oc, dt):
    i = 0
    while i < len(oc):
        if oc[i].last_traded >= dt:
            break
        i += 1

    back = front = i
    if i < len(oc)-1:
        back += 1

    return oc[front], oc[back]
