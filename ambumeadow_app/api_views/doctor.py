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
                "full_name": doctor.full_name,
                "phone_number": doctor.phone_number,
                "email": doctor.email,
                "role": doctor.role,
                "status": doctor.status,
                "phone_verified": doctor.phone_verified,
                "profile_image": doctor.profile_image,
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
