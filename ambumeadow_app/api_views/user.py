from .common_imports import *


# send expo_token -test api
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_expo_token(request, expo_token):
    send_push_notification(
        expo_token,
        "Test Notification",
        f"This is a test notification.",
        {"_id": 0}
    )
    return JsonResponse({"message":"Sent"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_notifications(request):
    try:
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-date')

        notification_list = []

        for notification in notifications:
            notification_list.append({
                "id": notification.id,
                "message": notification.message,
                "message_type": notification.message_type,
                "is_read": notification.is_read,
                "date": notification.date.strftime("%Y-%m-%d %H:%M:%S"),
            })

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return JsonResponse({
            "count": len(notification_list),
            "unread_count": unread_count,
            "notifications": notification_list,
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "message": "Failed to fetch notifications",
            "error": str(e)
        }, status=500)