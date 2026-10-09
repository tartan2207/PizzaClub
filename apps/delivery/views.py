from django.utils.decorators import method_decorator
from django_filters import FilterSet, CharFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from apps.delivery.models import Delivery
from apps.delivery.serializers import DeliverySerializer


class DeliveryFilter(FilterSet):
    courier = CharFilter(field_name='courier__username')

    class Meta:
        model = Delivery
        fields = ['phone', 'address',  'created_at', 'courier']


class DeliveryPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'

@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання списку доставок",
        operation_description=(
            "Повертає список доставок з підтримкою пагінації, фільтрації, пошуку та сортування.\n\n"
            "**Правила доступу:**\n"
            "- **Адміністратори**: бачать усі доставки в системі.\n"
            "- **Кур'єри**: бачать тільки доставки, де вони призначені виконавцями (`courier=user`).\n"
            "- **Клієнти**: бачать доставки, які відносяться до їхніх замовлень."
        ),
        responses={
            200: DeliverySerializer(many=True),
            401: "Неавторизований доступ (відсутній або недійсний JWT токен)",
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_summary="Отримання детальної інформації про доставку",
        operation_description="Повертає повну інформацію про конкретну доставку за її ID (якщо користувач має доступ).",
        responses={
            200: DeliverySerializer,
            401: "Неавторизований доступ",
            404: "Доставку не знайдено або немає прав для перегляду",
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Створення нової доставки",
        operation_description="Створює новий запис про доставку (адреса, телефон, кур'єр тощо).",
        request_body=DeliverySerializer,
        responses={
            201: DeliverySerializer,
            400: "Помилка валідації вхідних даних",
            401: "Неавторизований доступ",
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_summary="Часткове оновлення доставки",
        operation_description="Частково оновлює дані доставки (наприклад, зміна статусу, адреси чи кур'єра).",
        request_body=DeliverySerializer,
        responses={
            200: DeliverySerializer,
            400: "Помилка валідації вхідних даних",
            401: "Неавторизований доступ",
            404: "Доставку не знайдено",
        }
    )
)
class DeliveryViewSet(ModelViewSet):
    queryset = Delivery.objects.all().select_related('courier')
    serializer_class = DeliverySerializer
    filterset_class = DeliveryFilter
    pagination_class = DeliveryPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']

    ordering_fields = ['created_at']
    ordering = ['-created_at']
    search_fields = ['address', 'courier__first_name', 'courier__last_name', 'phone']

    def get_queryset(self):
        user = self.request.user
        queryset = Delivery.objects.select_related('courier').prefetch_related('order_deliveries')
        if not user.is_authenticated:
            return queryset.none()
        if user.is_staff or getattr(user, 'is_superuser', False):
            return queryset.all()
        return queryset.filter(courier=user) | queryset.filter(order_deliveries__customer=user).distinct()
