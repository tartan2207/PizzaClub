from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.account.models import CustomerUser
from apps.delivery.models import Delivery
from apps.dish.models import MenuDish
from apps.core.models import BaseModel

class Order(BaseModel):
    class OrderStatus(models.TextChoices):
        PENDING = "в обробці",
        PAID = "оплачен",
        DELIVERED = "доставлено",
        CANCELLED = "скасован"

    number = models.CharField(max_length=20, unique=True, editable=False)
    order_price = models.DecimalField(max_digits=9,
                                      decimal_places=2,
                                      default=Decimal('0.00'),
                                      validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        max_length=10
    )
    customer =models.ForeignKey(CustomerUser, on_delete=models.PROTECT, related_name='orders' )
    delivery = models.ForeignKey(Delivery, on_delete=models.PROTECT,related_name='order_deliveries')

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.number}"

    def save(self, *args, **kwargs):
        if not self.pk:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            date_str = timezone.now().strftime('%y%m%d')
            self.number = f"{date_str}-{self.id}"
            super().save(update_fields=['number'])
        else:
            super().save(*args, **kwargs)

    def recalculate_order_price(self):
        result = self.menus.aggregate(
            total=Sum('price_dish')
        )
        self.order_price = result['total'] or Decimal('0')
        self.save(update_fields=['order_price', 'updated_at'])
        return self.order_price


class MenuOrder(BaseModel):
    quantity= models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_dish = models.DecimalField(max_digits=9,
                                     decimal_places=2,
                                     null=True,
                                     validators=[MinValueValidator(Decimal('0.00'))])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='menus')
    menu = models.ForeignKey(MenuDish, on_delete=models.RESTRICT, related_name='menu_orders')

    def __str__(self) -> str:
        return f"{self.menu} x {self.quantity}"

    @property
    def get_price_dish(self):
        if not self.menu:
            return Decimal('0.00')
        return self.quantity*self.menu.final_price


