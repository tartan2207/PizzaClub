from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal

from django.contrib.sessions.backends.base import SessionBase
from rest_framework import status
from rest_framework.exceptions import APIException

from apps.dish.models import MenuDish

CART_SESSION_KEY = "cart"

class NotEnoughStock(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, menu_dish: MenuDish) -> None:
        dish_name = getattr(menu_dish, 'name', getattr(getattr(menu_dish, 'dish', None), 'name', 'Товар'))
        detail = f"На жаль, «{dish_name}» лишилось лише {menu_dish.stock} шт."
        super().__init__(detail=detail)
        self.menu_dish = menu_dish


@dataclass
class CartLine:
    menu_dish: MenuDish
    quantity: int

    @property
    def line_total(self) -> Decimal:
        if self.menu_dish is None:
            return Decimal('0.00')
        price = getattr(self.menu_dish, 'calculated_final_price', self.menu_dish.final_price)
        return price * self.quantity


class Cart:
    def __init__(self, session: SessionBase) -> None:
        self.session = session
        self.items: dict[str, int] = session.setdefault(CART_SESSION_KEY, {})

    def add(self, menu_dish: MenuDish, quantity: int = 1) -> None:
        current_qty = self.items.get(str(menu_dish.pk), 0)
        self.update(menu_dish, current_qty + quantity)

    def update(self, menu_dish: MenuDish, quantity: int) -> None:
        if quantity <= 0:
            self.remove(menu_dish)
            return

        if quantity > menu_dish.stock:
            raise NotEnoughStock(menu_dish)

        self.items[str(menu_dish.pk)] = quantity
        self.session.modified = True

    def remove(self, menu_dish: MenuDish) -> None:
        pk_str = str(menu_dish.pk)
        if pk_str in self.items:
            del self.items[pk_str]
            self.session.modified = True

    def clear(self) -> None:
        self.items.clear()
        self.session.modified = True

    def __iter__(self) -> Iterator[CartLine]:
        valid_pks = []
        for pk_str in list(self.items.keys()):
            try:
                valid_pks.append(int(pk_str))
            except (ValueError, TypeError):
                del self.items[pk_str]
                self.session.modified = True

        menu_dishes = MenuDish.objects.active().in_bulk(valid_pks)
        missing_pks = set(valid_pks) - set(menu_dishes.keys())
        if missing_pks:
            for pk in missing_pks:
                self.items.pop(str(pk), None)
            self.session.modified = True

        for pk_str, quantity in list(self.items.items()):
            menu_dish = menu_dishes.get(int(pk_str))
            if menu_dish is not None:
                yield CartLine(menu_dish, quantity)

    def __len__(self) -> int:
        return sum(self.items.values())

    @property
    def total(self) -> Decimal:
        return sum((line.line_total for line in self), Decimal("0.00"))