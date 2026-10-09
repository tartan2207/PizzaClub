from decimal import Decimal

from django.db.models import F, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions
from rest_framework.fields import DecimalField
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import (BooleanFilter,
                                           FilterSet,
                                           CharFilter,
                                           NumberFilter)
from rest_framework.viewsets import ModelViewSet

from apps.dish.models import MenuDish, Category
from apps.dish.serializers import MenuDishSerializer, CategorySerializer


class MenuDishFilter(FilterSet):
    category = CharFilter(field_name='category__slug', lookup_expr='exact')
    parent_category = CharFilter(
        field_name='category__parent__slug', lookup_expr='exact'
    )
    # Фильтрация по наличию (stock > 0)
    in_stock = BooleanFilter(method='filter_in_stock')

    over_final_price = NumberFilter(
        field_name='calculated_final_price', lookup_expr='gte'
    )
    less_final_price = NumberFilter(
        field_name='calculated_final_price', lookup_expr='lte'
    )
    class Meta:
        model = MenuDish
        fields = ['category',
                  'parent_category',
                  'in_stock',
                  'over_final_price',
                  'less_final_price' ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

# 2. Настраиваем Пагинацию для DRF
class MenuDishPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'

class MenuDishViewSet(ModelViewSet):
    queryset = MenuDish.objects.all().annotate(
        calculated_final_price=F('price') - Coalesce(
            'discount',
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).select_related('dish', 'category')
    serializer_class = MenuDishSerializer
    filterset_class = MenuDishFilter
    pagination_class = MenuDishPagination

    ordering_fields = ['created_at', 'dish__name', 'calculated_final_price']
    ordering = ['-created_at','dish__name' ]
    search_fields = ['dish__name', 'category__name', 'dish__description']

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    ordering_fields = ['name']
    ordering = ['name' ]
    search_fields = ['name', 'children__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Если пользователь ищет конкретную категорию по поиску (?search=...),
        # отключаем фильтр parent__isnull=True, чтобы найти подкатегорию, даже если она не корневая
        if self.request.query_params.get('search'):
            return Category.objects.all().prefetch_related('children')

        return queryset


# class DishPagination(PageNumberPagination):
#     page_size = 12
#     page_size_query_param = 'page_size'
#
# class DishViewSet(ModelViewSet):
#     queryset = Dish.objects.all().prefetch_related('menu_items__category')
#     serializer_class = DishSerializer
#     pagination_class = DishPagination
#
#     ordering_fields = [ 'name']
#     ordering = ['name' ]
#     search_fields = ['name', 'description', 'menu_items__category__name']



# class MenuDishDetailView(generics.RetrieveAPIView):
#     queryset = MenuDish.objects.all().select_related('dish', 'dish__category')
#     serializer_class = MenuDishSerializer





