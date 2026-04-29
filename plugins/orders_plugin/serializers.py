from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for individual order items with validation"""
    
    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_id', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']
    
    # ✅ INPUT VALIDATION
    def validate_product_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Product name cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Product name is too long (max 200 characters).")
        return value.strip()
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        if value > 10000:
            raise serializers.ValidationError("Quantity cannot exceed 10,000 units.")
        return value
    
    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        if value > 100000000:
            raise serializers.ValidationError("Unit price is too high.")
        return value


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order with multiple items"""
    
    user_id = serializers.IntegerField(min_value=1)
    items = OrderItemSerializer(many=True, min_length=1)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one product.")
        
        # Check for duplicate products
        product_names = [item['product_name'].lower() for item in value]
        if len(product_names) != len(set(product_names)):
            raise serializers.ValidationError("Cannot have duplicate products in the same order.")
        
        return value
    
    def validate(self, data):
        items = data.get('items', [])
        total_value = sum(item['quantity'] * item['unit_price'] for item in items)
        if total_value > 1000000000:
            raise serializers.ValidationError("Total order value exceeds maximum allowed (1,000,000,000 FCFA).")
        return data


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for displaying an order with all its items"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.username')
    customer_grade = serializers.ReadOnlyField(source='customer.grade')
    delivery_status = serializers.SerializerMethodField()

    def get_delivery_status(self, obj):
        try:
            from plugins.mrp_production_plugin.models import Production
            prods = Production.objects.filter(item__order=obj)
            if prods.exists():
                statuses = set(prods.values_list('delivery_status', flat=True))
                if 'pending' in statuses: return 'pending'
                if 'shipped' in statuses: return 'shipped'
                if 'delivered' in statuses: return 'delivered'
        except ImportError:
            pass
        return 'pending'

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'customer_grade', 'status', 'priority', 
            'total_amount', 'discount_applied', 'created_at', 
            'updated_at', 'expected_delivery_date', 'items', 'delivery_status'
        ]