from rest_framework import serializers
from .models import *

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
    
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class GetSingleProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class DeleteProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class UpdateProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = '__all__'