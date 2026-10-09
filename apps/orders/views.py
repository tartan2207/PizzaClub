from django.utils.decorators import method_decorator
from django_filters.rest_framework import filters, FilterSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.dish.models import MenuDish
from apps.orders.cart import Cart, NotEnoughStock
from apps.orders.models import Order, MenuOrder
from apps.orders.serializers import (OrderSerializer,
                              CartSerializer,
                              CartActionSerializer,
                              OrderCreateSerializer,
                              OrderStatusUpdateSerializer,
                              MenuOrderCreateSerializer,
                              MenuOrderSerializer,
                              MenuOrderQuantityUpdateSerializer)


class OrderFilter(FilterSet):
    status = filters.CharFilter(field_name='status')
    over_order_price = filters.NumberFilter(field_name='order_price', lookup_expr='gte')
    less_order_price = filters.NumberFilter(field_name='order_price', lookup_expr='lte')
    date_created = filters.DateFilter(field_name='created_at')

    class Meta:
        model = Order
        fields = ['status', 'over_order_price', 'less_order_price', 'created_at']

class OrderPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'

@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання списку замовлень",
        operation_description=(
            "Повертає список замовлень з пагінацією та фільтрацією. "
            "Звичайний користувач бачить тільки свої замовлення, а адміністратор — усі."
        ),
        responses={
            200: OrderSerializer(many=True),
            401: "Неавторизований доступ",
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_summary="Детальна інформація про замовлення",
        operation_description="Повертає повну інформацію про конкретне замовлення за його ID.",
        responses={
            200: OrderSerializer,
            401: "Неавторизований доступ",
            404: "Замовлення не знайдено",
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Створення нового замовлення",
        operation_description="Створює нове замовлення. Поля number та order_price розраховуються автоматично на сервері.",
        request_body=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: "Помилка валідації вхідних даних",
            401: "Неавторизований доступ",
        }
    )
)

@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_summary="Часткове оновлення замовлення (PATCH)",
        operation_description="Оновлює окремі поля замовлення (наприклад, статус ).",
        request_body=OrderStatusUpdateSerializer,
        responses={
            200: OrderSerializer,
            400: "Помилка валідації",
            401: "Неавторизований доступ",
            404: "Замовлення не знайдено",
        }
    )
)
class OrderViewSet(ModelViewSet):
    filterset_class = OrderFilter
    pagination_class = OrderPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post',  'patch']

    ordering_fields = ['created_at', 'order_price', 'status']
    ordering = ['-created_at']
    search_fields = ['number' ]

    def get_queryset(self):
        user = self.request.user
        # Базовый кверисетоптимизирован для чтения заказов со всеми вложенными объектами
        queryset = Order.objects.select_related(
            'customer', 'delivery', 'delivery__courier'
        ).prefetch_related('menu_orders__menu__dish')
        # Анонимные пользователи не видят заказов
        # if not user.is_authenticated:
        #     return queryset.none()
        if user.is_staff or user.is_superuser or getattr(user, 'is_admin', False):
            return queryset.all()
        return queryset.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Возвращаем детальную информацию о созданном заказе
        response_serializer = OrderSerializer(
            order, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )



class MenuOrderFilter(FilterSet):
    over_price_dish = filters.NumberFilter(field_name='price_dish', lookup_expr='gte')
    less_price_dish = filters.NumberFilter(field_name='price_dish', lookup_expr='lte')
    date_created = filters.DateFilter(field_name='created_at')
    class Meta:
        model = MenuOrder
        fields = [ 'over_price_dish', 'less_price_dish', 'date_created']

class MenuOrderPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'




@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання списку замовлених страв",
        operation_description="Повертає список позицій у замовленнях з пагінацією та фільтрацією.",
        responses={200: MenuOrderSerializer(many=True), 401: "Неавторизований доступ"}
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_summary="Детальна інформація про позицію замовлення",
        operation_description="Повертає повну інформацію про конкретне замовлення страви за його ID.",
        responses={200: MenuOrderSerializer, 401: "Неавторизований доступ", 404: "Не знайдено"}
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Додавання страви до замовлення",
        request_body=MenuOrderCreateSerializer,
        responses={201: MenuOrderSerializer, 400: "Помилка валідації", 401: "Неавторизований доступ"}
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_summary="Оновлення кількості страви",
        request_body=MenuOrderQuantityUpdateSerializer,
        responses={200: MenuOrderSerializer, 400: "Помилка валідації", 401: "Неавторизований доступ"}
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        operation_summary="Видалення страви із замовлення",
        responses={204: "Успішно видалено", 401: "Неавторизований доступ", 404: "Не знайдено"}
    )
)
class MenuOrderView(ModelViewSet):
    filterset_class = MenuOrderFilter
    pagination_class = MenuOrderPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    ordering_fields = ['created_at', 'price_dish']
    ordering = ['-created_at']
    search_fields = ['order__number']

    def get_queryset(self):
        user = self.request.user
        # Оптимизированный QuerySet: подтягиваем order, menu и блюдо
        queryset = MenuOrder.objects.select_related('order', 'menu__dish')
        if user.is_staff or user.is_superuser or getattr(user, 'is_admin', False):
            return queryset.all()
        # Фильтрация только по заказам текущего пользователя
        return queryset.filter(order__customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return MenuOrderCreateSerializer
        if self.action == 'partial_update':
            return MenuOrderQuantityUpdateSerializer
        return MenuOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_order = serializer.save()
        response_serializer = MenuOrderSerializer(
            menu_order, context=self.get_serializer_context()
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)




@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання вмісту кошика",
        responses={
            200: CartSerializer(),
            401: "Неавторизований доступ",
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Додавання товару до кошика",
        request_body=CartActionSerializer,
        responses={
            200: CartSerializer(),
            400: "Помилка валідації або недостатньо товару",
            401: "Неавторизований доступ",
        }
    )
)
class CartViewSet(viewsets.ViewSet):

        permission_classes = [permissions.IsAuthenticated]  # Доступен и анонимам, и авторизованным

        def get_cart(self) -> Cart:
            return Cart(self.request.session)

        def list(self, request):
            cart = self.get_cart()
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        def create(self, request):
            serializer = CartActionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            menu_dish_id = serializer.validated_data['menu_dish_id']
            quantity = serializer.validated_data['quantity']

            menu_dish = get_object_or_404(
                MenuDish.objects.active(), pk=menu_dish_id
            )

            cart = self.get_cart()
            try:
                cart.add(menu_dish=menu_dish, quantity=quantity)
            except NotEnoughStock as exc:
                return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        @action(detail=False, methods=['patch'], url_path='update-quantity')
        def update_quantity(self, request):
            serializer = CartActionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            menu_dish_id = serializer.validated_data['menu_dish_id']
            quantity = serializer.validated_data['quantity']

            menu_dish = get_object_or_404(
                MenuDish.objects.active(), pk=menu_dish_id
            )

            cart = self.get_cart()
            try:
                cart.update(menu_dish=menu_dish, quantity=quantity)
            except NotEnoughStock as exc:
                return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        @swagger_auto_schema(
            operation_summary="Видалення товару з кошика",
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'menu_dish_id': openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="ID страви"
                    )
                },
                required=['menu_dish_id']
            ),
            responses={200: CartSerializer()}
        )
        @action(detail=False, methods=['post'], url_path='remove-item')
        def remove_item(self, request):
            menu_dish_id = request.data.get('menu_dish_id')
            if not menu_dish_id:
                return Response(
                    {'detail': "Поле 'menu_dish_id' є обов'язковим."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            menu_dish = get_object_or_404(MenuDish, pk=menu_dish_id)
            cart = self.get_cart()
            cart.remove(menu_dish)

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        @swagger_auto_schema(
            operation_summary="Повне очищення кошика",
            responses={200: CartSerializer()}
        )
        @action(detail=False, methods=['delete'], url_path='clear')
        def clear(self, request):
            cart = self.get_cart()
            cart.clear()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)




    # @action(detail=True, methods=['patch'], url_path='update-status')
    # def update_status(self, request, pk=None):
    #     order = self.get_object()
    #     user = request.user
    #
    #     # 1. Проверка прав: менять статус могут только сотрудники или администраторы
    #     if not (user.is_staff or user.is_superuser or getattr(user, 'is_admin', False)):
    #         return Response(
    #             {'detail': 'У вас немає прав для зміни статусу замовлення.'},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )
    #
    #     new_status = request.data.get('status')
    #
    #     # 2. Валидация входных данных
    #     if not new_status:
    #         return Response(
    #             {'status': 'Поле status є обов\'язковим.'},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #
    #     # 3. Проверка на соответствие допустимым статусам из OrderStatus (TextChoices)
    #     valid_statuses = [s.value for s in Order.OrderStatus]
    #     if new_status not in valid_statuses:
    #         return Response(
    #             {
    #                 'status': f'Некоректний статус. Допустимі значення: {valid_statuses}'
    #             },
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #
    #     # 4. Обновление только конкретного поля
    #     order.status = new_status
    #     order.save(update_fields=['status'])
    #
    #     return Response(
    #         {
    #             'detail': f'Статус замовлення №{order.number} успішно змінено на "{order.get_status_display()}"',
    #             'status': order.status,
    #         },
    #         status=status.HTTP_200_OK,
    #     )


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = Cart(request.session)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """Добавить товар в корзину."""
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dish = get_object_or_404(MenuDish.objects.active(), pk=serializer.validated_data['menu_dish_id'])
        cart = Cart(request.session)
        cart.add(menu_dish=dish, quantity=serializer.validated_data['quantity'])

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Обновить количество товара в корзине."""
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dish = get_object_or_404(MenuDish.objects.active(), pk=serializer.validated_data['menu_dish_id'])
        cart = Cart(request.session)
        cart.update(menu_dish=dish, quantity=serializer.validated_data['quantity'])

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Удалить конкретный товар или очистить всю корзину."""
        cart = Cart(request.session)
        dish_id = request.data.get('menu_dish_id') or request.query_params.get('menu_dish_id')

        if dish_id:
            dish = get_object_or_404(MenuDish, pk=dish_id)
            cart.remove(dish)
        else:
            cart.clear()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)



