from decimal import Decimal

from rest_framework import serializers

from apps.dish.models import Dish, Category, MenuDish


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id','name', 'slug','parent', 'children']
        read_only_fields = ['id', 'slug']

    def get_children(self, instance: Category):
        # 2. Оптимизированное получение дочерних категорий без лишних SQL-запросов
        children = instance.children.all()
        if children:
            return CategorySerializer(
                children, many=True, context=self.context
            ).data
        return []

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model=Dish
        fields = ['id','name', 'description', 'image']

class MenuDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    # Так как в модели MenuDish у нас уже есть @ property def final_price,
    # использовать serializers.ReadOnlyField():
    final_price = serializers.ReadOnlyField()
    class Meta:
        model = MenuDish
        fields = ['id',
                  'dish',
                  'portion',
                  'price',
                  'final_price',
                  'slug',
                  'discount',
                  'stock',
                  'category']
        read_only_fields = ['id', 'is_active', 'slug']

    def validate_price(self, value):
            if value is None or value<Decimal('0.01'):
                raise serializers.ValidationError("Ціна товару повинна бути позитивною.")
            return value

    # def get_final_price (self, obj):
    #     if not obj or obj.price is None:
    #         return Decimal('0.01')
    #     discount = obj.discount or Decimal('0.00')
    #     return Decimal(obj.price)-Decimal(discount)

