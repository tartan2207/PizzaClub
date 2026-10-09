from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.dish.models import MenuDish
from apps.orders.models import Order
from apps.reviews.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(queryset=MenuDish.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id','comment', 'rating', 'menu','user', "created_at", 'user_username']
        read_only_fields = ['id', 'created_at']

        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['user', 'menu'],
                message="Ви вже залишали відгук для цього блюда.",
            )
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        menu_dish = attrs.get('menu') or getattr(self.instance, 'menu', None)
        if user and menu_dish:
            has_purchased = Order.objects.filter(
                customer=user,
                status=Order.OrderStatus.DELIVERED,
                menu_orders__menu=menu_dish
            ).exists()

            if not has_purchased:
                raise serializers.ValidationError(
                    {"menu": "Ви можете залишити відгук тільки після купівлі та получения цього блюда."}
                )

        return attrs

    def validate_rating(self,value)->int:
        if value is None or (value<1 or value >5):
            raise serializers.ValidationError("Оберіть оцінку від 1 до 5.")
        return value

    def get_user_username(self, review: Review) -> str:
        if review.user:
            return  review.user.username
        return "Анонім"
