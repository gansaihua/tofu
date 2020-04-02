"""
scrapy crawl czc
scrapy crawl czc -a t=20200401
scrapy crawl czc -a t=20200331 -a t2=20200402
"""
import re
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem


class CZCSpider(scrapy.Spider):
    name = 'czc'

    def start_requests(self):
        t = getattr(self, 't', 'today')       # start date
        t2 = getattr(self, 't2', None)        # end date

        if t2 is None:
            yield scrapy.Request(
                self._get_url(t),
                callback=self.parse,
                meta={'datetime': pd.Timestamp(t)},
            )
        else:
            for dt in pd.date_range(t, t2):
                print(dt)
                yield scrapy.Request(
                    self._get_url(dt),
                    callback=self.parse,
                    meta={'datetime': dt},
                )

    def _get_url(self, dt):
        dt = pd.Timestamp(dt)
        if dt >= pd.Timestamp('2015-10-01'):
            url = f'http://www.czce.com.cn/cn/DFSStaticFiles/Future/{dt:%Y}/{dt:%Y%m%d}/FutureDataDaily.htm'
        else:
            url = f'http://www.czce.com.cn/cn/exchange/{dt:%Y}/datadaily/{dt:%Y%m%d}.htm'
        return url

    def parse(self, response):
        dt = response.meta['datetime']

        try:
            if dt <= pd.Timestamp('2017-12-27'):
                df = pd.read_html(response.text,
                                  attrs={'id': 'senfe'},
                                  header=0)[0]
            else:
                df = pd.read_html(response.text)[0]
        except (ValueError, IndexError):
            return

        for _, item in df.iterrows():
            if re.match(r'^\w{2}\d{3}$', item['品种月份']):
                l = ItemLoader(item=BarItem(), selector=item)

                l.add_value('symbol', item['品种月份'])
                l.add_value('datetime', dt.strftime('%Y%m%d'))
                l.add_value('open', item['今开盘'])
                l.add_value('high', item['最高价'])
                l.add_value('low', item['最低价'])
                l.add_value('close', item['今收盘'])
                l.add_value('volume', item['成交量(手)'])
                l.add_value('open_interest', item['空盘量'])

                l.add_value('exchange', self.name)
                yield l.load_item()
