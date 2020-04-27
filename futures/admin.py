from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol')


@admin.register(models.RootSymbol)
class RootSymbolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'exchange', 'active')
    list_filter = ('active', 'exchange',)
    # ordering = ('exchange', 'name')


@admin.register(models.Contract)
class ContractAdmin(admin.ModelAdmin):
    def data(self):
        return format_html(
            f'''
            <a href="/admin/futures/dailybar/?contract_id={self.id}">
            +
            </a>
            '''
        )

    data.allow_tags = True

    def exchange(self):
        return self.root_symbol.exchange

    list_per_page = 31
    list_display = (
        'id', exchange, 'name', 'symbol',
        'margin', 'tick_size', 'multiplier', 'day_limit', 'delivery',
        'contract_issued', 'last_traded',
        data,
    )
    list_filter = ('active', 'root_symbol__exchange', 'root_symbol')
    search_fields = ('id', 'symbol', 'name')
    ordering = ('root_symbol__exchange', '-symbol')


@admin.register(models.DailyBar)
class DailyBarAdmin(admin.ModelAdmin):
    list_per_page = 31
    list_display = ('contract', 'datetime', 'open', 'high', 'low',
                    'close', 'volume', 'open_interest')
    list_filter = ('contract__root_symbol__exchange', 'contract__root_symbol')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
