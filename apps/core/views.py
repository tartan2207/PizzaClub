from django.db import connection
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_summary="Перевірка стану системи (Health Check)",
        operation_description=(
            "Перевіряє доступність REST API та стан підключення до бази даних PostgreSQL.\n"
            "Призначено для використання оркестраторами (Docker, Kubernetes) та балансувальниками навантаження."
        ),
        responses={
            200: openapi.Response(
                description="Система та база даних працюють штатно",
                examples={
                    "application/json": {
                        "healthy": True,
                        "database": "ok"
                    }
                }
            ),
            503: openapi.Response(
                description="Сервіс недоступний (помилка підключення до бази даних)",
                examples={
                    "application/json": {
                        "healthy": False,
                        "database": "unavailable"
                    }
                }
            )
        }
    )
)
class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        health_status = {
            "healthy": True,
            "database": "ok"
        }
        try:
            connection.ensure_connection()
        except Exception:
            health_status["healthy"] = False
            health_status["database"] = "unavailable"
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)