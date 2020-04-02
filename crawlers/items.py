import scrapy
import pandas as pd
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def _convert_to_date(dt):
    return pd.Timestamp(dt).date()


def _remove_nan(value):
    if not value.isnumeric():
        return None
    return value


class BarItem(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(str, str.strip),
        output_processor=Join(''),
    )
    symbol = scrapy.Field(
        input_processor=MapCompose(str, str.strip, str.upper),
        output_processor=Join(''),
    )
    exchange = scrapy.Field(
        input_processor=MapCompose(str.strip, str.upper),
        output_processor=TakeFirst(),
    )
    datetime = scrapy.Field(
        input_processor=MapCompose(str.strip, _convert_to_date),
        output_processor=TakeFirst(),
    )
    open = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    high = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    low = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    close = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    volume = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    open_interest = scrapy.Field(
        input_processor=MapCompose(str, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
