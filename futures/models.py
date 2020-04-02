from django.db import models


class Exchange(models.Model):
    # ('大商所', 'DCE')
    # ('上期所', 'SHF')
    # ('中金所', 'CFE')
    # ('郑商所', 'CZC')
    name = models.CharField(max_length=10, null=True, blank=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name}'


class Code(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=10)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    margin = models.FloatField(null=True, blank=True)
    day_limit = models.FloatField(null=True, blank=True)
    delivery = models.DateTimeField(null=True, blank=True)
    contract_issued = models.DateTimeField(null=True, blank=True)
    last_traded = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.symbol}.{self.exchange.symbol}'


class Bar(models.Model):
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    open_interest = models.IntegerField(null=True, blank=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code}.{self.datetime}'
