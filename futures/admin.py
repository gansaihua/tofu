from django.contrib import admin
from . import models


@admin.register(models.Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol')


@admin.register(models.Code)
class CodeAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = (
        'id', 'exchange', 'name', 'symbol', 'margin',
        'day_limit', 'delivery', 'contract_issued', 'last_traded',
    )
    list_filter = ('exchange',)
    ordering = ('exchange', 'symbol')


# @admin.register(models.Bar)
# class BarAdmin(admin.ModelAdmin):
#     list_per_page = 25
#     list_display = ('code', 'datetime', 'open', 'high', 'low',
#                     'close', 'volume', 'open_interest')
#     date_hierarchy = 'datetime'
#     ordering = ('-datetime',)
