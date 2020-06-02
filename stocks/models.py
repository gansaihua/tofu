from django.db import models

from futures.models import Exchange


class Code(models.Model):
    ASSET_TYPE = [
        (0, 'Stock'),
        (1, 'Stock Index'),
        (2, 'Bond Index'),
    ]

    symbol = models.CharField(max_length=30)
    exchange = models.ForeignKey(
        Exchange, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    asset = models.IntegerField(choices=ASSET_TYPE, default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}({self.symbol})'


class DayBar(models.Model):
    code = models.ForeignKey(Code,
                             on_delete=models.CASCADE,
                             unique_for_date='datetime')
    datetime = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)

    class Meta:
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
