"""
scrapy crawl sse
scrapy crawl sse -a s=000001
scrapy crawl sse -a s=000001 -a n=3 # download 3 bars
"""

import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from .. import models
from ..items import BarItem


class SWIndexpider(scrapy.Spider):
    name = 'swindex'
    exchange = None

    def start_requests(self):
        url_fmt = "http://www.swsindex.com/excel2.aspx?ctable=swindexhistory&where=swindexcode in ('{}')"

        t1 = getattr(self, 't1', None)
        if t1 is not None:
            t1 = pd.Timestamp(t1)
            url_fmt += f" and BargainDate>='{t1:%Y-%m-%d}'"

        t2 = getattr(self, 't2', None)
        if t2 is not None:
            t2 = pd.Timestamp(t2)
            url_fmt += f" and BargainDate<='{t2:%Y-%m-%d}'"

        symbols = getattr(self, 'symbol', None)
        if symbols is None:
            symbols = models.Code.objects.filter(symbol__endswith='SI')
            for s in symbols:
                print(s)

                s, suffix = s.symbol.split('.')
                yield scrapy.Request(url_fmt.format(s))
        else:
            s, suffix = symbols.split('.')
            yield scrapy.Request(url_fmt.format(s))

    def parse(self, response):
        df = pd.read_html(response.text)[0]
        for _, item in df.iterrows():
            l = ItemLoader(item=BarItem(), selector=item)

            symbol = '{:0>6}.SI'.format(str(item['指数代码']).strip())
            l.add_value('symbol', symbol)
            l.add_value('datetime', item['发布日期'])
            l.add_value('open', item['开盘指数'])
            l.add_value('high', item['最高指数'])
            l.add_value('low', item['最低指数'])
            l.add_value('close', item['收盘指数'])
            l.add_value('volume', item['成交量(亿股)']*1e8)
            l.add_value('amount', item['成交额(亿元)']*1e8)

            yield l.load_item()
