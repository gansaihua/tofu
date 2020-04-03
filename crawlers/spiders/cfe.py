"""
scrapy crawl cfe
scrapy crawl cfe -a t1=20100416
scrapy crawl cfe -a t1=20200331 -a t2=20200402
"""
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem


ALLOWED_PRODUCTS = {
    'IF': '沪深300指数期货',
    'IH': '上证50指数期货',
    'IC': '中证500指数期货',
    'TF': '5年期国债期货',
    'T': '10年期国债期货',
    'TS': '2年期国债期货',
}


class CFESpider(scrapy.Spider):
    name = 'cfe'

    def start_requests(self):
        t1 = getattr(self, 't1', 'today')
        t2 = getattr(self, 't2', 'today')

        url_fmt = 'http://www.cffex.com.cn/sj/hqsj/rtj/{}/index.xml'
        for dt in pd.date_range(t1, t2):
            print(dt)
            url = url_fmt.format(dt.strftime('%Y%m/%d'))
            yield scrapy.Request(url)

    def parse(self, response):
        items = response.css('dailydata')
        for item in items:
            code = item.css('productid::text').get().strip()
            if code in ALLOWED_PRODUCTS.keys():
                l = ItemLoader(item=BarItem(), selector=item)

                t = item.css('instrumentid::text').get().strip()
                l.add_value('name', ALLOWED_PRODUCTS[code])
                l.add_value('name', t[-4:])
                l.add_value('symbol', t)

                l.add_css('datetime', 'tradingday::text')
                l.add_css('open', 'openprice::text')
                l.add_css('high', 'highestprice::text')
                l.add_css('low', 'lowestprice::text')
                l.add_css('close', 'closeprice::text')
                l.add_css('volume', 'volume::text')
                l.add_css('open_interest', 'openinterest::text')

                l.add_value('exchange', self.name)
                yield l.load_item()
