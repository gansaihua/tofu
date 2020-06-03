from django.db import models

from futures.models import Exchange


class Code(models.Model):
    ASSET_TYPE = [
        (0, 'Stock'),
        (1, 'Stock Index'),
        (2, 'Bond Index'),
    ]
    MARKET_TYPE = [
        (0, '主板'),
        (1, '中小企业板'),
        (2, '创业板'),
        (3, '科创板'),
    ]

    symbol = models.CharField(max_length=30)
    wind_code = models.CharField(max_length=30, null=True, blank=True)
    exchange = models.ForeignKey(
        Exchange, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    asset = models.IntegerField(choices=ASSET_TYPE, default=0)
    market = models.IntegerField(choices=MARKET_TYPE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}({self.symbol})'


class DayBar(models.Model):
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('code', 'datetime')
        indexes = [models.Index(fields=['datetime'], name='daybar_dt_idx2')]
        get_latest_by = "datetime"

    def __str__(self):
        return f'{self.code}({self.datetime})'


class DayBar_Changes(models.Model):
    """Intermediate process for batch insert into DayBar model
    """
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    datetime = models.BigIntegerField()  # nano-seconds
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)


class Adjustment(models.Model):
    TYPE = [
        (0, 'adjustment factor'),
        (1, 'dividends'),
        (2, 'splits'),
    ]
    type = models.IntegerField(choices=TYPE, default=0)
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    value = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ('datetime',)
        get_latest_by = "datetime"
