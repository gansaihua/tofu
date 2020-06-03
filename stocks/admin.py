from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Code)
class CodeAdmin(admin.ModelAdmin):
    def dbar(self):
        return format_html(
            f'''
            <a href="/admin/stocks/daybar/?code_id={self.id}">
            +d
            </a>
            '''
        )

    def adj(self):
        return format_html(
            f'''
            <a href="/admin/stocks/adjustment/?code_id={self.id}">
            +
            </a>
            '''
        )

    dbar.allow_tags = True
    adj.allow_tags = True

    list_display = ('id', 'name', 'symbol', 'exchange',
                    'start_date',  'end_date', 'market',
                    'active', dbar, adj)
    list_filter = ('active', 'market', 'exchange', 'asset')
    search_fields = ('id', 'symbol', 'name')


@admin.register(models.DayBar)
class DayBarAdmin(admin.ModelAdmin):
    list_per_page = 31
    list_display = ('code', 'datetime', 'open', 'high', 'low',
                    'close', 'volume', 'amount')
    list_filter = ('code__exchange', 'code')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)


@admin.register(models.Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'datetime', 'value')
    list_filter = ('type', 'code')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
