from .common_imports import *


# get_notification api
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_notifications(request, user_id):
    try:
        user_id = User.objects.get(id=user_id)
        notifications = Notification.objects.filter(user=user_id, is_read=False).order_by('-date')
        serializer = NotificationSerializer(notifications, many=True)
        return JsonResponse(serializer.data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# end of get notification api