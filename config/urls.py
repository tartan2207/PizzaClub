
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="PizzaClub API",
        default_version='v1',
        description="API для PizzaClub проєкту",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@pizza-club.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],  # Кому дозволено доступ до документації
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.orders.urls')),
    path('', include('apps.reviews.urls')),
    path('', include('apps.delivery.urls')),
    path('', include('apps.delivery.urls')),
    path('', include('apps.account.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  ]
