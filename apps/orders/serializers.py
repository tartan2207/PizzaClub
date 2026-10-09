from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers

from apps.account.models import CustomerUser
from apps.account.serializers import CustomerUserSerializer
from apps.delivery.models import Delivery
from apps.delivery.serializers import DeliverySerializer
from apps.dish.models import MenuDish
from apps.dish.serializers import MenuDishSerializer
from apps.orders.cart import NotEnoughStock, Cart
from apps.orders.models import Order, MenuOrder

class OrderSerializer(serializers.ModelSerializer):
    delivery=DeliverySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer = CustomerUserSerializer(read_only=True)
    class Meta:
        model= Order
        fields = ['id', 'number', 'status_display', 'order_price', 'customer', 'delivery','created_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    delivery_id = serializers.PrimaryKeyRelatedField(
        queryset=Delivery.objects.all(), source='delivery', write_only=True
    )
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomerUser.objects.all(), source='customer', write_only=True
    )

    class Meta:
        model = Order
        fields = [ 'delivery_id','customer_id']

    def validate(self, attrs):
        request = self.context.get('request')
        cart = Cart(request.session)
        if len(cart) == 0:
            raise serializers.ValidationError({"cart": "Ваша корзина пуста."})
        for line in cart:
            if line.quantity > line.menu_dish.stock:
                raise NotEnoughStock(line.menu_dish)

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        cart = Cart(request.session)
        with transaction.atomic():
            order = Order.objects.create(
                customer=user,
                delivery=validated_data['delivery'],
                order_price=cart.total,
                status=Order.OrderStatus.PENDING,
            )

            order_items = []
            for line in cart:
                menu_dish = MenuDish.objects.select_for_update().get(
                    pk=line.menu_dish.pk
                )

                if line.quantity > menu_dish.stock:
                    raise NotEnoughStock(menu_dish)
                menu_dish.stock -= line.quantity
                menu_dish.save(update_fields=['stock'])
                order_items.append(
                    MenuOrder(
                        order=order,
                        menu=menu_dish,
                        quantity=line.quantity,
                        price=line.menu_dish.final_price,
                    )
                )
            MenuOrder.objects.bulk_create(order_items)
            cart.clear()
            return order



class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Order.OrderStatus.choices)
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class MenuOrderSerializer(serializers.ModelSerializer):
    menu = MenuDishSerializer(read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    price_dish = serializers.DecimalField(
        max_digits=9, decimal_places=2, source='get_price_dish', read_only=True
    )

    class Meta:
        model=MenuOrder
        fields = ['id', 'quantity', 'price_dish', 'order_id', 'menu', 'created_at']
        read_only_fields = ['price_dish', 'created_at']
class MenuOrderCreateSerializer(serializers.ModelSerializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuDish.objects.all(), source='menu', write_only=True
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source='order', write_only=True
    )

    class Meta:
        model = MenuOrder
        fields = [ 'menu_id','order_id', 'quantity', ]

class MenuOrderQuantityUpdateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    class Meta:
        model = MenuOrder
        fields = ['quantity']

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price_dish = instance.quantity * instance.menu.final_price
        instance.save()
        return instance



class CartItemSerializer(serializers.Serializer):
    menu_dish_id = serializers.IntegerField(source='menu_dish.id', read_only=True)
    name = serializers.CharField(
        source='menu_dish.dish.name', default='', read_only=True
    )
    price = serializers.DecimalField(
        source='menu_dish.final_price', max_digits=10, decimal_places=2, read_only=True
    )
    quantity = serializers.IntegerField(read_only=True)
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, source='*')
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(
        source='total', max_digits=10, decimal_places=2, read_only=True
    )

    def get_total_quantity(self, obj: Cart) -> int:
        return len(obj)

class CartActionSerializer(serializers.Serializer):
    menu_dish_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(default=1, min_value=1)


