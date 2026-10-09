from django.contrib import admin

from apps.orders.models import Order, MenuOrder

class MenuOrderInline(admin.TabularInline):
    model = MenuOrder
    extra = 0
    fields = ('menu', 'quantity', 'price_dish', 'get_menu_stock')
    readonly_fields = ('get_menu_stock',)
    ordering = ['menu__dish__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('menu__dish')


    @admin.display(description='Stock')
    def get_menu_stock(self, obj):
        if obj and obj.menu:
            return obj.menu.stock
        return '-'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'order_price','status','get_delivery_address',
                    'get_delivery_type', 'get_delivery_courier','created_at')
    ordering = ['-created_at']
    search_fields = ('number', )
    list_filter = ('status',)
    readonly_fields = ( 'created_at',)
    date_hierarchy = 'created_at'
    list_select_related = ('delivery',)
    inlines = [MenuOrderInline]

    @admin.display(description='Адрес доставки')
    def get_delivery_address(self, obj):
        return obj.delivery.address if obj.delivery else '-'

    @admin.display(description='Тип доставки')
    def get_delivery_type(self, obj):
        return obj.delivery.delivery_type if obj.delivery else '-'

    @admin.display(description='Courier')
    def get_delivery_courier(self, obj):
        if obj.delivery and obj.delivery.courier:
            return obj.delivery.courier
        return '-'

