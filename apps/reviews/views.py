from django.utils.decorators import method_decorator
from django_filters import FilterSet, CharFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from apps.core.permission import IsAdminOrOwnerReadOnly
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer

class ReviewFilter(FilterSet):
    menu = CharFilter(field_name='menu__dish__name')
    user = CharFilter(field_name='user__username')

    class Meta:
        model = Review
        fields = ['comment', 'rating']

class ReviewPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання списку відгуків",
        operation_description="Повертає список усіх відгуків з пагінацією та фільтрацією."
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Створення відгуку",
        operation_description="Залишити відгук може тільки покупцеві, який придбав це блюдо."
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_summary="Оновлення відгуку",
        operation_description="Редагувати відгук може тільки його автор."
    )
)
@method_decorator(
    name='destroy',
    decorator=swagger_auto_schema(
        operation_summary="Видалення відгуку",
        operation_description="Видалити відгук можуть тільки адміністратори."
    )
)
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    pagination_class = ReviewPagination
    permission_classes = [IsAdminOrOwnerReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    search_fields = ['user__username', 'menu__dish__name']

    def get_queryset(self):
        return Review.objects.select_related('menu__dish', 'user')


