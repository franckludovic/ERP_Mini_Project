from rest_framework import serializers
from .models import *

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
    
class addOrRemoveProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    class Meta:
        model = Product
        fields = '__all__'


# -------- MATERIAL --------
class MaterialSerializer(serializers.ModelSerializer):
    supplier = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Material
        fields = '__all__'

class GetSingleMaterialSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class DeleteMaterialSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class UpdateMaterialSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Material
        fields = '__all__'
    
class addOrRemoveMaterialSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    class Meta:
        model = Material
        fields = '__all__'

# -------- SUPPLIER --------
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class GetSingleSupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class DeleteSupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class UpdateSupplierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Supplier
        fields = '__all__'