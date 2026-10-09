from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.delivery.views import DeliveryViewSet

app_name = 'delivery'

router = DefaultRouter()
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
urlpatterns = [
    path('', include(router.urls)),
]