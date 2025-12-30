from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone

from ambumeadow_app.models import Hospital
from . auth import verify_firebase_token

# api to add hospital
@api_view(['POST'])
# @verify_firebase_token
def add_hospital(request):
    hospital_name = request.data.get("hospital_name")
    email = request.data.get("email", "")
    phone_number = request.data.get("phone_number")
    emergency_contact = request.data.get("emergency_contact", "")
    latitude = request.data.get("latitude", 0.0)
    longitude = request.data.get("longitude", 0.0)

    # basic validation
    if not hospital_name or not phone_number:
        return JsonResponse(
            {"message": "Hospital name and phone number are required"},
            status=400
        )

    # prevent duplicates
    if Hospital.objects.filter(phone_number=phone_number).exists():
        return JsonResponse(
            {"message": "Hospital with this phone number already exists"},
            status=409
        )

    try:
        hospital = Hospital.objects.create(
            hospital_name=hospital_name,
            email=email,
            phone_number=phone_number,
            emergency_contact=emergency_contact,
            latitude=latitude,
            longitude=longitude,
        )

        return JsonResponse({
            "message": "Hospital added successfully",
            "hospital": {
                "id": hospital.id,
                "hospital_name": hospital.hospital_name,
                "email": hospital.email,
                "phone_number": hospital.phone_number,
                "emergency_contact": hospital.emergency_contact,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "date_joined": hospital.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to add hospital", "error": str(e)},
            status=500
        )
# end of add hospital api


# api to get all hospitals
@api_view(['GET'])
# @verify_firebase_token
def get_all_hospitals(request):
    try:
        hospitals = Hospital.objects.all().order_by('-date_joined')

        hospital_list = []
        for hospital in hospitals:
            hospital_list.append({
                "id": hospital.id,
                "hospital_name": hospital.hospital_name,
                "email": hospital.email,
                "phone_number": hospital.phone_number,
                "emergency_contact": hospital.emergency_contact,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "date_joined": hospital.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({
            "count": len(hospital_list),
            "hospitals": hospital_list
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to fetch hospitals", "error": str(e)},
            status=500
        )
# end of get all hospitals api