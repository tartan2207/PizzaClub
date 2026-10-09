from rest_framework import serializers

from apps.account.serializers import CustomerUserSerializer
from apps.delivery.models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    courier = CustomerUserSerializer(read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    class Meta:
        model = Delivery
        fields = ['id',
                  'address',
                  'phone',
                  'delivery_type_display',
                  'courier',
                  'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.courier:
            representation['courier'] = {
                'id': instance.courier.id,
                'first_name': instance.courier.first_name,
                'last_name':  instance.courier.last_name,
                'phone': getattr(instance.courier, 'phone', None),
            }
        return representation