from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.account.models import CustomerUser
from apps.core.models import BaseModel
from apps.dish.models import MenuDish

class Review(BaseModel):
    comment=models.TextField(blank=True)
    rating = models.PositiveIntegerField(validators=[
        MinValueValidator(1,message="Оцінка не може бути меншою за 1."),
        MaxValueValidator(5,message="Оцінка не може бути більшою за 5."),
    ])
    menu=models.ForeignKey(MenuDish, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "menu"], name="unique_user_menu_dish_review")
        ]

    def __str__(self) -> str:
        return f"{self.user} на {self.menu.dish}: {self.rating}"
