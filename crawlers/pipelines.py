from . import models


class SQLPipeline(object):
    def process_item(self, item, spider):
        if item is None:
            return
        exchange, _ = models.Exchange.objects.get_or_create(
            symbol=item['exchange']
        )

        code, _ = models.Code.objects.update_or_create(
            exchange=exchange,
            symbol=item['symbol'],
            defaults={'name': item.get('name')},
        )

        models.Bar.objects.update_or_create(
            code=code,
            defaults={
                'datetime': item['datetime'],
                'open': item.get('open'),
                'high': item.get('high'),
                'low': item.get('low'),
                'close': item.get('close'),
                'volume': item.get('volume', 0),
                'open_interest': item.get('open_interest', 0),
            }
        )
