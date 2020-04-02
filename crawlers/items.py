import scrapy
import pandas as pd
from w3lib.html import remove_tags
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def convert_to_date(dt):
    return pd.Timestamp(dt).date()


def str_convert(s):
    return f'{s}'


class BarItem(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join(''),
    )
    symbol = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip, str.upper),
        output_processor=Join(''),
    )
    exchange = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip, str.upper),
        output_processor=TakeFirst(),
    )
    datetime = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip, convert_to_date),
        output_processor=TakeFirst(),
    )
    open = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    high = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    low = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    close = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    volume = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
    open_interest = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=TakeFirst(),
    )
