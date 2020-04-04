import pandas as pd
from . import models

# If we are only within `LOOKBACK` of the the front contract's last traded
# date, we will infer the primary contract
LOOKBACK = 10


def get_rolls(root_symbol,
              start_date=None,
              end_date=None,
              lookback=LOOKBACK):

    def _key_dates():
        ret = set()
        for code in oc:
            for i in range(lookback):
                dt = code.last_traded - pd.Timedelta(days=i)
                if dt <= end_date and dt >= start_date:
                    ret.add(dt)
        return ret

    oc = ordered_contracts(root_symbol)
    assert len(oc) > 2, 'Unsupported root symbol!'

    product_date = oc[0].contract_issued
    if start_date is None:
        start_date = product_date
    else:
        start_date = pd.Timestamp(start_date)

    if end_date is None:
        end_date = pd.Timestamp('today')
    else:
        end_date = pd.Timestamp(end_date)

    selected_dates = _key_dates()
    if start_date == product_date:
        selected_dates.add(product_date)

    dts = []
    ids = []
    for dt in selected_dates:
        tmp = primary_contract(root_symbol, dt)
        if tmp.id not in ids:
            ids.append(tmp.id)
            dts.append(dt)

    return pd.Series(data=ids, index=dts)


# If we are within `GRACE_DAYS` of the front contract's last traded
# date, and a volume flip happened during that period, return the back
# contract as the active one.
GRACE_DAYS = 3


def primary_contract(root_symbol, dt, exchange=None, grace_days=GRACE_DAYS):
    # we need to make sure dt is a trading session
    dt = pd.Timestamp(dt)

    oc = ordered_contracts(root_symbol, exchange)
    front, back = _get_contracts_to_roll(oc, dt)

    back_bars = _lookup_bars(back, dt, grace_days)
    grace_days = min(grace_days, len(back_bars))

    front_bars = _lookup_bars(front, dt, grace_days)

    # If we are within `GRACE_DAYS` of the front contract's auto close
    # date, and a volume flip happened during that period, return the back
    # contract as the active one.
    for i in range(1, grace_days):
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

    symbol = models.Code.objects.get(
        symbol__iexact=symbol,
        root_symbol__exchange__symbol__iexact=exchange
    )
    return symbol


def ordered_contracts(root_symbol, exchange=None):
    if not isinstance(root_symbol, models.ContinuousFutures):

        if exchange is None:
            root_symbol, exchange = root_symbol.split('.')

        root_symbol = models.ContinuousFutures.objects.get(
            symbol__iexact=root_symbol,
            exchange__symbol__iexact=exchange
        )

    symbol = models.Code.objects.filter(root_symbol=root_symbol)
    return symbol.order_by('last_traded')


def _get_contracts_to_roll(oc, dt):
    n = len(oc)
    i = 0
    while i < n:
        if oc[i].last_traded >= dt:
            break
        i += 1

    back = front = i
    if i != n - 1:
        back += 1

    return oc[front], oc[back]


def _lookup_bars(symbol, dt, offset, exchange=None):
    code = lookup_contract(symbol, exchange)
    qs = models.Bar.objects.filter(
        code=code,
        datetime__lte=dt,
    ).order_by('-datetime')
    return qs[:offset]
