import json
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from ambumeadow_app.models import Hospital, Ambulance
from . auth import verify_firebase_token
from django.http import JsonResponse

from ambumeadow_app.api_serializers.ambulance import NearestAmbulanceSerializer
from ambumeadow_app.utils.distance import haversine

# api to add ambulance
@csrf_exempt
@api_view(['POST'])
def add_ambulance(request):
    if request.method != 'POST':
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        data = request.data
        hospital_id = data.get("hospital_id")
        driver_id = data.get("driver_id")
        plate_number = data.get("plate_number")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not all([hospital_id, driver_id, plate_number]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        # check if hospital exists
        hospital = Hospital.objects.filter(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"message": "Hospital not found"}, status=404)
        # check if ambulance with same plate number exists
        existing_ambulance = Ambulance.objects.filter(plate_number=plate_number).first()
        if existing_ambulance:
            return JsonResponse({"message": "Ambulance with this plate number already exists"}, status=400)
        
        # check if driver exists
        driver = Driver.objects.filter(id=driver_id).first()
        if not driver:
            return JsonResponse({"message": "Driver not found"}, status=404)

        # Save Ambulance
        ambulance = Ambulance.objects.create(
            hospital_id=hospital,
            driver_id=driver,
            plate_number=plate_number,
            latitude=latitude,
            longitude=longitude
        )


        return JsonResponse({"message": "Ambulance added successfully."}, status=201)

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "Failed to add ambulance", "error": str(e)}, status=400)

#end of adding ambulance api


# get nearest ambulance api
@api_view(["POST"])
def get_nearest_ambulances(request):
    """
    Expects:
    {
        "lat": -1.2921,
        "lng": 36.8219
    }
    """

    lat = request.data.get("latitude")
    lng = request.data.get("longitude")

    if lat is None or lng is None:
        return Response(
            {"error": "Latitude and longitude are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ambulances = Ambulance.objects.filter(
        is_available=True,
        current_lat__isnull=False,
        current_lng__isnull=False,
    )

    results = []

    for ambulance in ambulances:
        distance = haversine(
            float(lat),
            float(lng),
            ambulance.current_lat,
            ambulance.current_lng,
        )

        ambulance.distance_km = round(distance, 2)
        results.append(ambulance)

    # sort by nearest
    results.sort(key=lambda x: x.distance_km)

    serializer = NearestAmbulanceSerializer(results, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
# end of getting nearest ambulance api