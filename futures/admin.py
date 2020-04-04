from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Roll)
class RollAdmin(admin.ModelAdmin):
    list_per_page = 31
    list_display = ('root_symbol', 'datetime', 'code', 'verion')
    list_filter = ('verion', 'root_symbol', 'root_symbol__exchange')
    ordering = ('-datetime',)


@admin.register(models.Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol')


@admin.register(models.ContinuousFutures)
class ContinuousFuturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'exchange')
    list_filter = ('exchange',)
    ordering = ('exchange', 'name')


@admin.register(models.Code)
class CodeAdmin(admin.ModelAdmin):
    def data(self):
        return format_html(
            f'''
            <a href="/admin/futures/bar/?code_id={self.id}">
            +
            </a>
            '''
        )

    data.allow_tags = True

    def exchange(self):
        return self.root_symbol.exchange

    list_per_page = 31
    list_display = (
        'id', exchange, 'name', 'symbol', 'margin',
        'day_limit', 'delivery', 'contract_issued', 'last_traded',
        data,
    )
    list_filter = ('root_symbol', 'root_symbol__exchange')
    search_fields = ('id', 'symbol', 'name')
    ordering = ('root_symbol__exchange', '-symbol')


@admin.register(models.Bar)
class BarAdmin(admin.ModelAdmin):
    list_per_page = 31
    list_display = ('code', 'datetime', 'open', 'high', 'low',
                    'close', 'volume', 'open_interest')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
