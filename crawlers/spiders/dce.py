"""
scrapy crawl dce
scrapy crawl dce -a t1=20060104
scrapy crawl dce -a t1=20200331 -a t2=20200402
"""
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader

from ..items import BarItem


ALLOWED_PRODUCTS = {
    '豆一': 'A',
    '豆二': 'B',
    '豆粕': 'M',
    '豆油': 'Y',
    '棕榈油': 'P',
    '玉米': 'C',
    '玉米淀粉': 'CS',
    '鸡蛋': 'JD',
    '粳米': 'RR',
    '纤维板': 'FB',
    '胶合板': 'BB',
    '聚乙烯': 'L',
    '聚氯乙烯': 'V',
    '聚丙烯': 'PP',
    '苯乙烯': 'EB',
    '焦炭': 'J',
    '焦煤': 'JM',
    '铁矿石': 'I',
    '乙二醇': 'EG',
    '液化石油气': 'PG',
}


class DCESpider(scrapy.Spider):
    name = 'dce'

    def start_requests(self):
        t1 = getattr(self, 't1', 'today')
        t2 = getattr(self, 't2', 'today')

        url = 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
        data = {'dayQuotes.variety': 'all',
                'dayQuotes.trade_type': '0'}

        for dt in pd.date_range(t1, t2):
            print(dt)
            data['year'] = f'{dt.year}'
            data['month'] = f'{dt.month-1}'
            data['day'] = f'{dt.day}'
            yield scrapy.FormRequest(url, formdata=data)

    def parse(self, response):
        try:
            df = pd.read_html(response.text, na_values=['-'])[0]
        except (ValueError, IndexError):
            return

        for _, item in df.iterrows():
            if item['商品名称'].strip() in ALLOWED_PRODUCTS.keys():
                l = ItemLoader(item=BarItem(), response=response)

                calendar = self._sanitize_calendar(item['交割月份'])
                l.add_value('symbol', ALLOWED_PRODUCTS[item['商品名称']])
                l.add_value('symbol', calendar)
                l.add_value('name', item['商品名称'])
                l.add_value('name', calendar)
                l.add_css('datetime', '#currDate::attr(value)')
                l.add_value('open', item['开盘价'])
                l.add_value('high', item['最高价'])
                l.add_value('low', item['最低价'])
                l.add_value('close', item['收盘价'])
                l.add_value('volume', item['成交量'])
                l.add_value('open_interest', item['持仓量'])
                l.add_value('exchange', self.name)
                yield l.load_item()

    def _sanitize_calendar(self, calendar):
        """
        calendar: '2007.0', '202007.0'
        return: '2007'
        """
        return str(int(float(calendar)))[-4:]
