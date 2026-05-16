from .common_imports import *

# api to get all staffs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_staffs(request):
    staffs = Staff.objects.all()
    staff_data = []
    for staff in staffs:
        staff_data.append({
            "id": staff.id,
            "full_name": staff.full_name,
            "phone_number": staff.phone_number,
            "email": staff.email,
            "status": staff.status,
            "role": staff.role,
            "department": staff.department,
            "date_joined": staff.date_joined,
        })
    return JsonResponse({"staffs": staff_data})

# end of get all staffs api


# delete staff
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_staff(request):
    staff_id = request.data.get('staff_id')
    try:
        staff = Staff.objects.get(id=staff_id)

        if not staff:
            return Response({"error": "Staff not found"}, status=404)

        # delete user in firebase
        firebase_uid = staff.firebase_uid
        if firebase_uid:
            auth.delete_user(firebase_uid)
        
        staff.delete()

        return Response({"message": "Staff deleted successfully"})
    except Staff.DoesNotExist:
        return Response({"error": "Staff not found"}, status=404)

# end of deleter staff api


# Activate / Suspend staff
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_staff_status(request):
    staff_id = request.data.get('staff_id')
    status = request.data.get('status')
    try:
        staff = Staff.objects.get(id=staff_id)
        if not staff:
            return Response({"error": "Staff not found"}, status=404)

        staff.status = status
        staff.save()
        return Response({
            "message": "Status updated",
            "status": staff.status
        })
    except Staff.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of toggle staff api