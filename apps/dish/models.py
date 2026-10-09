from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import OuterRef, Sum, Subquery, IntegerField, Avg, Count
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import BaseModel



class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=300, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return f"{reverse('dish:menu_list')}?category={self.slug}"

class Dish(BaseModel):
    name = models.CharField(max_length=200, verbose_name = 'Назва')
    description = models.TextField(verbose_name= 'Опис')
    image = models.ImageField("image",upload_to="menu/", blank=True, null=True)
    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self) -> str:
        return self.name

class MenuDishQuerySet(models.QuerySet):
    def is_active(self):
        return self.filter(is_active=True)

    def in_stock(self):
        return self.filter(stock__gt=0)

    def with_sold(self):
        from apps.dish.apps import MenuOrder, Order
        sold = (
            MenuOrder.objects.filter(menu=OuterRef("pk")
            )
            .exclude(order__status=Order.OrderStatus.CANCELLED)
            .values("menu")
            .annotate(total=Sum("quantity"))
            .values("total")  # Вытаскиваем только сумму
        )
        return self.annotate(
            sold_qty=Coalesce(Subquery(sold, output_field=IntegerField()), 0)
        )

    def with_rating(self):
       return self.annotate(
            rating_avg=Coalesce(Avg("reviews__rating"), 0.0),
            rating_count=Count("reviews", distinct=True),
        )

    def for_listing(self):
        return (
            self.is_active()
            .select_related("category")
            .with_rating()
            .with_sold()
            .order_by("-created_at", "-id")
        )

class MenuDish(BaseModel):
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    portion= models.CharField(max_length=7)
    price = models.DecimalField(max_digits=9,
                                decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=9,
                                   decimal_places=2,
                                   default=Decimal('0.00'),
                                   validators=[MinValueValidator(Decimal('0.00'))])
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='menu_items')
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_dishes', null=True)

    objects = MenuDishQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.dish.name} ({self.portion})"

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(f"{self.dish.name}-{self.portion}")
        super().save(*args, **kwargs)


    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def final_price(self)->Decimal:
        if self.discount > Decimal('0.00'):
            return max(self.price - self.discount, Decimal('0.00'))
        return self.price

    # 2. Валидация данных перед сохранением
    def clean(self):
        super().clean()
        if self.discount and self.discount > self.price:
            raise ValidationError({'discount': 'Скидка не может быть больше стоимости блюда.'})

    def get_absolute_url(self) -> str:
        return reverse("dish:menu_detail", kwargs={"slug": self.slug})





