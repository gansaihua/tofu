"""
scrapy crawl szse
scrapy crawl szse -a s=000001
scrapy crawl szse -a s=000001 -a n=100
"""

import json
import scrapy
from scrapy.loader import ItemLoader
from .. import models
from ..items import BarItem


class SZSESpider(scrapy.Spider):
    name = 'szse'
    exchange = 'SZSE'

    def start_requests(self):
        self.n_bar = getattr(self, 'n', 2)
        symbols = getattr(self, 'symbol', None)

        url_fmt = 'http://www.szse.cn/api/market/ssjjhq/getHistoryData?cycleType=32&marketId=1&code={}'
        if symbols is None:
            symbols = models.Code.objects.filter(
                exchange__symbol=self.exchange)
            for s in symbols:
                print(s)
                yield scrapy.Request(url_fmt.format(s.symbol))
        else:
            yield scrapy.Request(url_fmt.format(symbols))

    def parse(self, response):
        js = json.loads(response.text)['data']

        data = js['picupdata']
        if data is None:
            return

        n = len(data)
        for i, item in enumerate(data):
            if i < max(0, n - self.n_bar):  # skip the first n bars
                continue

            l = ItemLoader(item=BarItem(), selector=item)

            l.add_value('symbol', js['code'])
            l.add_value('datetime', item[0])
            l.add_value('open', item[1])
            l.add_value('high', item[4])
            l.add_value('low', item[3])
            l.add_value('close', item[2])
            l.add_value('volume', item[7])
            l.add_value('amount', item[8])

            yield l.load_item()
