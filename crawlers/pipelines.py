import re
from . import models


class SQLPipeline(object):
    def process_item(self, item, spider):
        if item is None:
            return

        exchange, _ = models.Exchange.objects.get_or_create(
            symbol=item['exchange']
        )

        root_symbol = re.match(r'^(\w{1,2}?)\d{4}$', item['symbol']).group(1)
        root_symbol, _ = models.ContinuousFutures.objects.get_or_create(
            symbol=root_symbol,
            exchange=exchange,
        )

        code, _ = models.Code.objects.update_or_create(
            root_symbol=root_symbol,
            symbol=item['symbol'],
            defaults={
                'name': item.get('name'),
            },
        )

        models.Bar.objects.update_or_create(
            code=code,
            datetime=item['datetime'],
            defaults={
                'open': item.get('open'),
                'high': item.get('high'),
                'low': item.get('low'),
                'close': item.get('close'),
                'volume': item.get('volume', 0),
                'open_interest': item.get('open_interest', 0),
            }
        )
