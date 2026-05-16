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