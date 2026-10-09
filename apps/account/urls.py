from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import  TokenRefreshView

from apps.account.views import RegisterViewSet, CustomerUserViewSet, CustomTokenObtainPairView

app_name = 'account'

router = DefaultRouter()
router.register(r'users', CustomerUserViewSet, basename='user')
router.register(r'auth/register', RegisterViewSet, basename='register')

urlpatterns = [
    # 🔑 Эндпоинты авторизации JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Эндпоинты из ViewSet'ов
    path('', include(router.urls)),
]