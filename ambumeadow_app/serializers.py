from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Notification
        fields = ['id', 'message', 'message_type', 'date', 'is_read']