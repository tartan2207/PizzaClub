from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dish.views import MenuDishViewSet, CategoryViewSet

app_name = 'dish'

router = DefaultRouter()
router.register(r'menu', MenuDishViewSet, basename='menu')
router.register(r'categories', CategoryViewSet, basename='category')
urlpatterns = [
    path('', include(router.urls)),
]