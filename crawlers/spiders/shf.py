"""
scrapy crawl shf
scrapy crawl shf -a t=20200401
scrapy crawl shf -a t=20200331 -a t2=20200402
"""
import json
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem


class SHFSpider(scrapy.Spider):
    name = 'shf'

    def start_requests(self):
        t = getattr(self, 't', 'today')       # start date
        t2 = getattr(self, 't2', None)        # end date

        url_fmt = 'http://www.shfe.com.cn/data/dailydata/kx/kx{}.dat'
        t = pd.Timestamp(t).strftime('%Y%m%d')
        if t2 is None:
            yield scrapy.Request(url_fmt.format(t), callback=self.parse)
        else:
            for dt in pd.date_range(t, t2):
                url = url_fmt.format(dt.strftime('%Y%m%d'))
                yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        try:
            js = json.loads(response.text)
        except json.JSONDecodeError:
            return

        for item in js['o_curinstrument']:
            try:  # Skip the summary rows
                int(item['DELIVERYMONTH'])
            except ValueError:
                continue

            l = ItemLoader(item=BarItem(), selector=item)

            l.add_value('symbol', item['PRODUCTID'], re=r'(.+)_.+')
            l.add_value('symbol', item['DELIVERYMONTH'])
            l.add_value('name', item['PRODUCTNAME'])
            l.add_value('name', item['DELIVERYMONTH'])
            l.add_value('datetime', js['report_date'])
            l.add_value('open', item['OPENPRICE'])
            l.add_value('high', item['HIGHESTPRICE'])
            l.add_value('low', item['LOWESTPRICE'])
            l.add_value('close', item['CLOSEPRICE'])
            l.add_value('volume', item['VOLUME'])
            l.add_value('open_interest', item['OPENINTEREST'])
            l.add_value('exchange', self.name)
            yield l.load_item()
