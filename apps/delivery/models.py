from django.conf import settings
from django.db import models

from apps.core.models import BaseModel



class Delivery(BaseModel):
    class DeliveryType(models.TextChoices):
        PICKUP = "самовивіз",
        COURIER = "курьер"

    address = models.TextField(max_length=300)
    phone = models.CharField(max_length=20)
    courier = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                related_name='deliveries',
                                null=True,
                                blank=True )
    delivery_type = models.CharField(max_length=10,
                                     choices=DeliveryType.choices,
                                     default=DeliveryType.COURIER,
                                     blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.address} {self.delivery_type}"
