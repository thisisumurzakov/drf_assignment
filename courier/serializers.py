from rest_framework import serializers
from .models import Courier, Order

class CourierSerializer(serializers.ModelSerializer):
    regions = serializers.ListField(child=serializers.IntegerField())
    working_hours = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Courier
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    delivery_hours = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Order
        fields = ('id', 'delivery_hours', 'weight', 'region')