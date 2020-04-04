"""
scrapy crawl czc
scrapy crawl czc -a t1=20050509
scrapy crawl czc -a t1=20200331 -a t2=20200402
"""
import re
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem

DEFAULT_MIN_DATE = pd.Timestamp('2005-05-09')
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
        t1 = getattr(self, 't1', 'today')
        t2 = getattr(self, 't2', 'today')

        if pd.Timestamp(t1) < DEFAULT_MIN_DATE:
            t1 = DEFAULT_MIN_DATE

        for dt in pd.date_range(t1, t2):
            print(dt)
            url = self._get_url(dt)
            yield scrapy.Request(url, meta={'datetime': dt})

    def parse(self, response):
        dt = response.meta['datetime']
        df = self._read_table(response, dt)

        for _, item in df.iterrows():
            if re.match(r'^\w{2}\d{3}$', item['contract']):
                symbol = self._sanitize_code(item['contract'], dt)

                if symbol[:2] in ALLOWED_PRODUCTS.keys():
                    l = ItemLoader(item=BarItem(), selector=item)

                    l.add_value('symbol', symbol)
                    l.add_value('name', ALLOWED_PRODUCTS[symbol[:2]])
                    l.add_value('name', symbol[2:])
                    l.add_value('datetime', dt.strftime('%Y%m%d'))
                    l.add_value('open', item['open'])
                    l.add_value('high', item['high'])
                    l.add_value('low', item['low'])
                    l.add_value('close', item['close'])
                    l.add_value('volume', item['volume'])
                    l.add_value('open_interest', item['open_interest'])
                    l.add_value('exchange', self.name)

                    yield l.load_item()

    def _sanitize_code(self, raw_code, dt):
        """
        raw_code: 'FG911', 'LR007'
        return: 'FG1911', 'LR2007'
        """
        ref = dt.strftime('%y%m')

        calendar = ref[0] + raw_code[2:]
        if int(calendar) < int(ref):
            calendar = str(int(calendar) + 1000)

        symbol = raw_code[:2]
        return symbol + calendar

    def _get_url(self, dt):
        """
        Handle different version API
        changed after 2015-10-01, 2010-08-25
        """
        if dt >= pd.Timestamp('2015-10-01'):
            url = f'http://www.czce.com.cn/cn/DFSStaticFiles/Future/{dt:%Y}/{dt:%Y%m%d}/FutureDataDaily.htm'
        elif dt >= pd.Timestamp('2010-8-25'):
            url = f'http://www.czce.com.cn/cn/exchange/{dt:%Y}/datadaily/{dt:%Y%m%d}.htm'
        else:
            url = f'http://www.czce.com.cn/cn/exchange/jyxx/hq/hq{dt:%Y%m%d}.html'
        return url

    def _read_table(self, response, dt):
        """
        Handle different web page structure
        changed after 2017-12-28, 2010-08-25
        """
        if dt >= pd.Timestamp('2017-12-28'):
            df = pd.read_html(response.text)[0]
            df.rename(columns={
                '品种月份': 'contract',
                '今开盘': 'open',
                '最高价': 'high',
                '最低价': 'low',
                '今收盘': 'close',
                '成交量(手)': 'volume',
                '空盘量': 'open_interest',
            }, inplace=True)
        elif dt >= pd.Timestamp('2010-8-25'):
            df = pd.read_html(response.text,
                              attrs={'id': 'senfe'},
                              header=0)[0]
            df.rename(columns={
                '品种月份': 'contract',
                '今开盘': 'open',
                '最高价': 'high',
                '最低价': 'low',
                '今收盘': 'close',
                '成交量(手)': 'volume',
                '空盘量': 'open_interest',
            }, inplace=True)
        else:
            df = pd.read_html(response.text)[1]
            df.rename(columns={
                '品种月份': 'contract',
                '今开盘': 'open',
                '最高价': 'high',
                '最低价': 'low',
                '今收盘': 'close',
                '成交量': 'volume',
                '空盘量': 'open_interest',
            }, inplace=True)
        return df
