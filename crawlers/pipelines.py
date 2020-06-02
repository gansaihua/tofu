import re
import pandas as pd

from . import models


class FuturesPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        # check compatible spiders
        if crawler.spider.name in ('cfe', 'czc', 'dce', 'ine', 'shf'):
            return cls()

    def open_spider(self, spider):
        # TODO!
        # use batch insert mode, will not update
        if getattr(spider, 'batch', False):
            self.batch_mode = True
        else:
            self.batch_mode = False

    def process_item(self, item, spider):
        if item is None:
            return

        exchange = models.Exchange.objects.get(symbol=item['exchange'])

        _symbol = re.match(r'^(\w{1,2}?)\d{4}$', item['symbol']).group(1)
        _name = re.match(r'^(\w+)\d{4}$', item['name']).group(1)
        root_symbol, _ = models.RootSymbol.objects.get_or_create(
            symbol=_symbol,
            exchange=exchange,
            defaults={'name': _name},
        )

        contract, _ = models.Contract.objects.get_or_create(
            root_symbol=root_symbol,
            symbol=item['symbol'],
            defaults={
                'name': item['name'],
                # for temporary use
                # will rewrite by update_contract command
                'contract_issued': pd.Timestamp('today').normalize(),
                'last_traded': pd.Timestamp('2050-1-1'),
            },
        )

        models.FuturesDayBar.objects.update_or_create(
            contract=contract,
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


class StockPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        # check compatible spiders
        if crawler.spider.name in ('sse', 'szse'):
            return cls()

    def open_spider(self, spider):
        # TODO!
        # use batch insert mode, will not update
        if getattr(spider, 'batch', False):
            self.batch_mode = True
        else:
            self.batch_mode = False

    def process_item(self, item, spider):
        exchange = getattr(spider, 'exchange', None)
        if exchange:
            code = models.Code.objects.get(
                symbol=item['symbol'],
                exchange__symbol=exchange,
            )
        else:  # swindex, citics index and etc
            code = models.Code.objects.get(symbol=item['symbol'])

        models.StockDayBar.objects.update_or_create(
            code=code,
            datetime=item['datetime'],
            defaults={'open': item.get('open'),
                      'high': item.get('high'),
                      'low': item.get('low'),
                      'close': item.get('close'),
                      'volume': item.get('volume', 0),
                      'amount': item.get('amount', 0)})
