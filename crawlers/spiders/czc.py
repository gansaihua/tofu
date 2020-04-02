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


ALLOWED_PRODUCTS = {
    'CF': '棉花',
    'ER': '早籼',
    'RO': '菜油',
    'SR': '白糖',
    'TA': 'PTA',
    'WS': '强麦',
    'WT': '硬麦',
    'ME': '甲醇',
    'OI': '菜油',
    'RI': '早籼',
    'WH': '强麦',
    'FG': '玻璃',
    'PM': '普麦',
    'RS': '油菜籽',
    'RM': '菜籽粕',
    'TC': '动力煤',
    'ZC': '动力煤',
    'JR': '粳稻',
    'MA': '甲醇',
    'LR': '晚籼',
    'SF': '硅铁',
    'SM': '锰硅',
    'CY': '棉纱',
    'AP': '苹果',
    'CJ': '红枣',
    'UR': '尿素',
    'SA': '纯碱',
}


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

        # API changed after 2015-10-01
        if dt >= pd.Timestamp('2015-10-01'):
            url = f'http://www.czce.com.cn/cn/DFSStaticFiles/Future/{dt:%Y}/{dt:%Y%m%d}/FutureDataDaily.htm'
        else:
            url = f'http://www.czce.com.cn/cn/exchange/{dt:%Y}/datadaily/{dt:%Y%m%d}.htm'
        return url

    def parse(self, response):
        dt = response.meta['datetime']

        try:  # web page structure changed after 2017-12-27
            if dt <= pd.Timestamp('2017-12-27'):
                df = pd.read_html(response.text, attrs={
                                  'id': 'senfe'}, header=0)
            else:
                df = pd.read_html(response.text)

            df = df[0]
        except (ValueError, IndexError):
            return

        for _, item in df.iterrows():
            if re.match(r'^\w{2}\d{3}$', item['品种月份']):
                code, t = item['品种月份'][:2], item['品种月份'][2:]
                if code in ALLOWED_PRODUCTS.keys():
                    l = ItemLoader(item=BarItem(), selector=item)
                    l.add_value('symbol', item['品种月份'])
                    l.add_value('name', ALLOWED_PRODUCTS[code])
                    l.add_value('name', t)
                    l.add_value('datetime', dt.strftime('%Y%m%d'))
                    l.add_value('open', item['今开盘'])
                    l.add_value('high', item['最高价'])
                    l.add_value('low', item['最低价'])
                    l.add_value('close', item['今收盘'])
                    l.add_value('volume', item['成交量(手)'])
                    l.add_value('open_interest', item['空盘量'])

                    l.add_value('exchange', self.name)
                    yield l.load_item()
