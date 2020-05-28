from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol')


@admin.register(models.RootSymbol)
class RootSymbolAdmin(admin.ModelAdmin):
    def cf_chain(self):
        return format_html(
            f'''
            <a href="/admin/futures/continuousfutures/?root_symbol__id={self.id}">
            ~
            </a>
            '''
        )
    cf_chain.allow_tags = True

    list_display = ('id', 'name', 'symbol', 'exchange',
                    'launched', 'active', cf_chain)
    list_filter = ('active', 'exchange')
    # ordering = ('exchange', 'name')


@admin.register(models.ContinuousFutures)
class ContinuousFuturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'root_symbol', 'contract', 'datetime', 'version')
    list_filter = ('root_symbol',)
    date_hierarchy = 'datetime'


@admin.register(models.Contract)
class ContractAdmin(admin.ModelAdmin):
    def exchange(self):
        return self.root_symbol.exchange

    def dbar(self):
        return format_html(
            f'''
            <a href="/admin/futures/dailybar/?contract_id={self.id}">
            +d
            </a>
            '''
        )

    def mbar(self):
        return format_html(
            f'''
            <a href="/admin/futures/minutebar/?contract_id={self.id}">
            +m
            </a>
            '''
        )

    dbar.allow_tags = True
    mbar.allow_tags = True

    list_per_page = 31
    list_display = (
        'id', exchange, 'name', 'symbol',
        'margin', 'tick_size', 'multiplier', 'day_limit', 'delivery',
        'contract_issued', 'last_traded',
        dbar, mbar,
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


@admin.register(models.MinuteBar)
class MinuteBarAdmin(admin.ModelAdmin):
    list_per_page = 60
    list_display = ('contract', 'datetime', 'open', 'high', 'low',
                    'close', 'volume', 'open_interest')
    list_filter = ('contract__root_symbol__exchange', 'contract__root_symbol')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
