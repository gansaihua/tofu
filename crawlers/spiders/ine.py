"""
scrapy crawl ine
scrapy crawl ine -a t1=20180326
scrapy crawl ine -a t1=20200331 -a t2=20200402
"""
import json
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem


DEFAULT_MIN_DATE = pd.Timestamp('2018-03-26')
ALLOWED_PRODUCTS = {
    'SC': '原油',
    'NR': '20号胶',
}


class INESpider(scrapy.Spider):
    name = 'ine'

    def start_requests(self):
        t1 = getattr(self, 't1', 'today')
        t2 = getattr(self, 't2', 'today')

        if pd.Timestamp(t1) < DEFAULT_MIN_DATE:
            t1 = DEFAULT_MIN_DATE

        url_fmt = 'http://www.ine.cn/data/dailydata/kx/kx{}.dat'
        for dt in pd.date_range(t1, t2):
            print(dt)
            url = url_fmt.format(dt.strftime('%Y%m%d'))
            yield scrapy.Request(url)

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

            if item['PRODUCTNAME'].strip() in ALLOWED_PRODUCTS.values():
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
