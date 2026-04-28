from rest_framework import serializers
from .models import *

class ProductMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source='material.name')
    material_stock = serializers.ReadOnlyField(source='material.quantity_in_stock')
    
    class Meta:
        model = ProductMaterial
        fields = ['material', 'material_name', 'material_stock', 'quantity_required']

class ProductSerializer(serializers.ModelSerializer):
    materials = ProductMaterialSerializer(source='productmaterial_set', many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity_in_stock', 'unit_price', 'materials']

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
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        required=False,
        allow_null=True
    )
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
        default="Nexus Internal"
    )

    class Meta:
        model = Material
        fields = ['id', 'name', 'quantity_in_stock', 'unit_price', 'supplier', 'supplier_name']

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