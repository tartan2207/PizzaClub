from django.contrib import admin

from apps.dish.models import Dish, MenuDish, Category

class MenuDishInline(admin.TabularInline):
    model= MenuDish
    extra = 1

    fields = ('portion','final_price','price','discount', 'stock', 'created_at',  'get_category')
    readonly_fields = ('created_at', 'final_price')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('dish', 'dish__category')

    @admin.display(
        description='Category',
        ordering='dish__category__name',
    )
    def get_category(self, obj):
        if obj and obj.dish and obj.dish.name:
            return obj.dish.category.name
        else:
            return '-'

    def final_price(self, obj):
        if not obj or obj.price is None:
            return "-"
        discount = obj.discount or 0
        return obj.price - discount


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    ordering = ['name']
    search_fields = ('name','description')
    inlines = [MenuDishInline]

    actions = ['deactivate_menu']

@admin.register(MenuDish)
class MenuDishAdmin(admin.ModelAdmin):
    list_display = ('dish','portion','price','final_price','discount', 'stock', 'created_at', 'get_category')
    ordering = ['dish__name']
    search_fields = ('dish__name', )
    list_filter = ('stock',)
    readonly_fields = ('created_at','final_price','get_category')
    date_hierarchy = 'created_at'
    list_select_related = ('dish','dish__category')

    def final_price(self, obj):
        if not obj or obj.price is None:
            return "-"
        discount = obj.discount or 0
        return obj.price - discount

    def get_category(self, obj):
        return obj.dish.category.name if obj.dish.category else '-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    prepopulated_fields = {"slug": ["name"]}





