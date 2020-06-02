import scrapy
import pandas as pd
from w3lib.html import remove_tags
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def _convert_to_date(dt):
    return pd.Timestamp(dt).date()


def _remove_nan(value):
    if value in ('nan', ''):
        return None
    return value


def _remove_zero(value):
    if value in ['0', '0.0', '0.00']:
        return None
    return value


def _convert_to_int(value):
    return int(float(value))


class BarItem(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip),
        output_processor=Join(''),
    )
    symbol = scrapy.Field(
        input_processor=MapCompose(str, remove_tags, str.strip, str.upper),
        output_processor=Join(''),
    )
    exchange = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip, str.upper),
        output_processor=TakeFirst(),
    )
    datetime = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _convert_to_date),
        output_processor=TakeFirst(),
    )
    open = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _remove_zero),
        output_processor=TakeFirst(),
    )
    high = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _remove_zero),
        output_processor=TakeFirst(),
    )
    low = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _remove_zero),
        output_processor=TakeFirst(),
    )
    close = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _remove_zero),
        output_processor=TakeFirst(),
    )
    volume = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _convert_to_int),
        output_processor=TakeFirst(),
    )
    amount = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan),
        output_processor=TakeFirst(),
    )
    open_interest = scrapy.Field(
        input_processor=MapCompose(
            str, remove_tags, str.strip, _remove_nan, _convert_to_int),
        output_processor=TakeFirst(),
    )
