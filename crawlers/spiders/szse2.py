"""
scrapy crawl szse
scrapy crawl szse -a s=000001
"""

import json
import scrapy
from scrapy.loader import ItemLoader
from .. import models
from ..items import BarItem


class SZSESpider(scrapy.Spider):
    name = 'szse2'
    exchange = 'SZSE'

    def start_requests(self):
        symbols = getattr(self, 'symbol', None)

        url_fmt = 'http://www.szse.cn/api/market/ssjjhq/getTimeData?marketId=1&code={}'
        if symbols is None:
            symbols = models.Code.objects.filter(active=True,
                                                 exchange__symbol=self.exchange)
            for s in symbols:
                print(s)
                yield scrapy.Request(url_fmt.format(s.symbol))
        else:
            yield scrapy.Request(url_fmt.format(symbols))

    def parse(self, response):
        print(response)
        js = json.loads(response.text)

        if js['code'] != 0:
            return

        data = js['data']

        l = ItemLoader(item=BarItem(), selector=item)

        l.add_value('symbol', data['code'])
        l.add_value('datetime', js['datetime'][:10])
        l.add_value('open', data['open'])
        l.add_value('high', data['high'])
        l.add_value('low', data['low'])
        l.add_value('close', data['now'])  # `close` is previous closing price
        l.add_value('volume', data['volume'])
        l.add_value('amount', data['amount'])

        return l.load_item()
