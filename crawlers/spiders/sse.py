"""
scrapy crawl sse
scrapy crawl sse -a s=000001
scrapy crawl sse -a s=000001 -a n=3 # download 3 bars
"""

import json
import scrapy
from scrapy.loader import ItemLoader
from .. import models
from ..items import BarItem


class SSESpider(scrapy.Spider):
    name = 'sse'
    exchange = 'SSE'

    def start_requests(self):
        n_bar = getattr(self, 'n', '1')
        symbols = getattr(self, 'symbol', None)

        n_begin = str(-int(n_bar) - 1)

        url_fmt = 'http://yunhq.sse.com.cn:32041//v1/sh1/dayk/{}?begin={}'
        if symbols is None:
            symbols = models.Code.objects.filter(
                exchange__symbol=self.exchange)
            for s in symbols:
                print(s)
                yield scrapy.Request(url_fmt.format(s.symbol, n_begin))
        else:
            yield scrapy.Request(url_fmt.format(symbols, n_begin))

    def parse(self, response):
        js = json.loads(response.text)

        for item in js['kline']:
            l = ItemLoader(item=BarItem(), selector=item)

            l.add_value('symbol', js['code'])
            l.add_value('datetime', item[0])
            l.add_value('open', item[1])
            l.add_value('high', item[2])
            l.add_value('low', item[3])
            l.add_value('close', item[4])
            l.add_value('volume', item[5])
            l.add_value('amount', item[6])

            yield l.load_item()
