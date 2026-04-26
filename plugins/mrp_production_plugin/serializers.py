from rest_framework import serializers
from .models import BOM, Production

class BOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOM
        fields = '__all__'

class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = '__all__'
