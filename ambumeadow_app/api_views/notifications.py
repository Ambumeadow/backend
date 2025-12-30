import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ambumeadow_app.models import User, Notification
from . auth import verify_firebase_token
from ambumeadow_app.serializers import NotificationSerializer
from django.http import JsonResponse


# get_notification api
@api_view(['GET'])
@verify_firebase_token
def get_user_notifications(request, user_id):
    try:
        user_id = User.objects.get(id=user_id)
        notifications = Notification.objects.filter(user=user_id, is_read=False).order_by('-date')
        serializer = NotificationSerializer(notifications, many=True)
        return JsonResponse(serializer.data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# end of get notification api