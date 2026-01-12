import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response

from ambumeadow_app.models import User
from .auth import verify_firebase_token
from firebase_admin import auth

# api to get all users
@api_view(['GET'])
# @verify_firebase_token
def get_all_users(request):
    users = User.objects.all()
    user_data = []
    for user in users:
        user_data.append({
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
        })
    return JsonResponse({"users": user_data})

# end of get all users api


# delete user
@api_view(['DELETE'])
# @verify_firebase_token
def delete_user(request):
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)

        if not user:
            return Response({"error": "User not found"}, status=404)

        # delete user in firebase
        firebase_uid = user.firebase_uid
        if firebase_uid:
            auth.delete_user(firebase_uid)
        
        user.delete()

        return Response({"message": "User deleted successfully"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of deleter user api


# Activate / Suspend user
@api_view(['PATCH'])
# @verify_firebase_token
def toggle_user_status(request):
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return Response({"error": "User not found"}, status=404)

        user.is_active = not user.is_active
        user.save()
        return Response({
            "message": "Status updated",
            "is_active": user.is_active
        })
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of toggle user api