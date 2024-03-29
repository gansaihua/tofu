from django.db import models


class Exchange(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)
    symbol = models.CharField(max_length=10)

    class Meta:
        ordering = ('symbol',)
        db_table = 'exchange'

    def __str__(self):
        return f'{self.symbol}'


class RootSymbol(models.Model):
    COMMISSION_TYPE = [
        (0, 'Percent'),
        (1, 'Fixed'),
    ]

    name = models.CharField(max_length=25, null=True, blank=True)
    symbol = models.CharField(max_length=3)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    launched = models.DateTimeField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)
    tick_size = models.FloatField(null=True, blank=True)
    multiplier = models.FloatField(null=True, blank=True)
    commission = models.FloatField(null=True, blank=True)
    commission_type = models.IntegerField(choices=COMMISSION_TYPE, default=0)

    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('symbol',)

    def __str__(self):
        return f'{self.symbol}'


class Contract(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=10)
    symbol_temp = models.CharField(  # for CZC use
        max_length=10, null=True, blank=True)
    root_symbol = models.ForeignKey(
        RootSymbol, on_delete=models.CASCADE)
    margin = models.FloatField(null=True, blank=True)
    day_limit = models.FloatField(null=True, blank=True)
    delivery = models.DateTimeField(null=True, blank=True)
    contract_issued = models.DateTimeField(null=True, blank=True)
    last_traded = models.DateTimeField(null=True, blank=True)
    tick_size = models.FloatField(null=True, blank=True)
    multiplier = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.symbol}.{self.root_symbol.exchange.symbol}'


class Chain(models.Model):
    root_symbol = models.ForeignKey(
        RootSymbol, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    version = models.IntegerField()

    class Meta:
        ordering = ('datetime',)
        get_latest_by = "datetime"


class DailyBar(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    open_interest = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('contract', 'datetime')
        indexes = [models.Index(fields=['datetime'], name='daybar_dt_idx')]
        get_latest_by = "datetime"

    def __str__(self):
        return f'{self.contract}.{self.datetime}'


class DailyBarChange(models.Model):
    """Intermediate process for batch insert into DailyBar model
    """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    datetime = models.BigIntegerField()  # nano-seconds
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    open_interest = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'futures_dailybar_changes'


class MinuteBar(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    open_interest = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('contract', 'datetime')
        indexes = [models.Index(fields=['datetime'], name='minbar_dt_idx')]
        get_latest_by = "datetime"

    def __str__(self):
        return f'{self.contract}.{self.datetime}'


class MinuteBarChange(models.Model):
    """Intermediate process for batch insert into MinuteBar model
    """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    datetime = models.BigIntegerField()  # nano-seconds
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    open_interest = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'futures_minutebar_changes'
