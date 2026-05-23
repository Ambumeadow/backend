from .common_imports import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_doctors(request):
    try:
        doctors = Staff.objects.filter(
            role='doctor',
            status='active'
        ).order_by('-date_joined')

        doctor_list = []

        for doctor in doctors:
            doctor_list.append({
                "id": doctor.id,
                "full_name": doctor.user.full_name,
                "phone_number": doctor.user.phone_number,
                "email": doctor.user.email,
                "role": doctor.role,
                "hospital": doctor.hospital.hospital_name,
                "department": doctor.department,
                "status": doctor.status,
                "phone_verified": doctor.user.phone_verified,
                "profile_image": doctor.user.profile_image,
                "date_joined": doctor.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({
            "count": len(doctor_list),
            "doctors": doctor_list
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to fetch doctors", "error": str(e)},
            status=500
        )
