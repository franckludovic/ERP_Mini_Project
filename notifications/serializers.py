from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationRequestSerializer(serializers.Serializer):
    event = serializers.CharField()
    user_id = serializers.IntegerField(required=False)
    data = serializers.DictField(required=False)