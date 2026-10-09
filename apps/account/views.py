from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
from .serializers import (
    CustomerUserSerializer,
    UserRegisterSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary="Отримання списку користувачів",
        operation_description=(
            "Повертає список користувачів.\n"
            "- **Адміністратори**: бачать усіх користувачів.\n"
            "- **Звичайні користувачі**: бачать тільки свій профіль."
        ),
        responses={
            200: CustomerUserSerializer(many=True),
            401: "Неавторизований доступ",
        }
    )
)
@method_decorator(
    name='retrieve',
    decorator=swagger_auto_schema(
        operation_summary="Отримання профілю користувача за ID",
        operation_description="Повертає інформацію про конкретного користувача за його ID.",
        responses={
            200: CustomerUserSerializer,
            401: "Неавторизований доступ",
            403: "Немає доступу до профілю другого користувача",
            404: "Користувача не знайдено",
        }
    )
)
@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Створення нового користувача",
        operation_description="Створює новий акаунт користувача.",
        request_body=CustomerUserSerializer,
        responses={
            201: CustomerUserSerializer,
            400: "Помилка валідації вхідних даних",
            401: "Неавторизований доступ",
        }
    )
)
@method_decorator(
    name='partial_update',
    decorator=swagger_auto_schema(
        operation_summary="Часткове оновлення профілю за ID",
        operation_description="Оновлює окремі поля профілю користувача за його ID.",
        request_body=CustomerUserSerializer,
        responses={
            200: CustomerUserSerializer,
            400: "Помилка валідації",
            401: "Неавторизований доступ",
            404: "Користувача не знайдено",
        }
    )
)

class CustomerUserViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerUserSerializer
    http_method_names = ['get', 'post', 'patch', 'put']

    def get_queryset(self):
        user = self.request.user
        # Администраторы видят всех, обычные пользователи — только себя
        if user.is_staff or user.is_superuser or getattr(user, 'is_admin', False):
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=['get', 'patch', 'put'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Эндпоинт /api/v1/users/me/ для получения и редактирования собственного профиля."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        operation_summary="Реєстрація нового користувача",
        operation_description="Створює новий обліковий запис користувача. Доступно для незареєстрованих відвідувачів.",
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response(
                description="Користувача успішно зареєстровано",
                schema=UserRegisterSerializer
            ),
            400: "Помилка валідації вхідних даних (наприклад, логін/email вже зайняті або паролі не збігаються)"
        }
    )
)
class RegisterViewSet(ModelViewSet):
    """Отдельный эндпоинт для регистрации нового пользователя."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = [ 'post']

class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомний ендпоінт авторизації (Login)."""
    serializer_class = CustomTokenObtainPairSerializer


