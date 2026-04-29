from rest_framework import serializers
from .models import BOM, Production

class BOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOM
        fields = '__all__'

class ProductionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='item.product_name', read_only=True)
    order_id = serializers.IntegerField(source='item.order.id', read_only=True)
    quantity = serializers.IntegerField(source='item.quantity', read_only=True)
    priority_level = serializers.CharField(source='item.order.priority', read_only=True)
    
    class Meta:
        model = Production
        fields = [
            'id', 'item', 'status', 'priority_level', 
            'delivery_status', 'start_date', 'product_name', 
            'order_id', 'quantity'
        ]
