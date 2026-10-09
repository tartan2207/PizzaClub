from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.views import OrderViewSet, MenuOrderView,CartViewSet

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'menu_orders', MenuOrderView, basename='menu_order')
router.register(r'cart', CartViewSet, basename='cart')
urlpatterns = [
    path('', include(router.urls)),
]






