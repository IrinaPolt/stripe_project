from django.contrib import admin
from .models import Item, Price, Order, PriceInOrder, Tax, Discount


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate']
    list_filter = ['name', ]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'size']
    list_filter = ['name', 'size']


class PriceInlineAdmin(admin.TabularInline):
    model = Price
    extra = 0


class PriceInOrderInlineAdmin(admin.TabularInline):
    model = PriceInOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [PriceInOrderInlineAdmin, ]
    ordering = ['-id', ]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [PriceInlineAdmin, ]
    list_display = ['name', 'description']
    list_filter = ['name', ]
