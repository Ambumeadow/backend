import json
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from ambumeadow_app.models import Hospital, Ambulance
from . auth import verify_firebase_token
from django.http import JsonResponse

from . auth import verify_firebase_token

from ambumeadow_app.api_serializers.ambulance import NearestAmbulanceSerializer
from ambumeadow_app.utils.distance import haversine

# api to add ambulance
@csrf_exempt
@api_view(['POST'])
# @verify_firebase_token
def add_ambulance(request):
    if request.method != 'POST':
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        data = request.data
        hospital_id = data.get("hospital_id")
        plate_number = data.get("plate_number")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not all([hospital_id, plate_number]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        # check if hospital exists
        hospital = Hospital.objects.filter(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"message": "Hospital not found"}, status=404)
        # check if ambulance with same plate number exists
        existing_ambulance = Ambulance.objects.filter(plate_number=plate_number).first()
        if existing_ambulance:
            return JsonResponse({"message": "Ambulance with this plate number already exists"}, status=400)
        

        # Save Ambulance
        ambulance = Ambulance.objects.create(
            hospital=hospital,
            plate_number=plate_number,
            current_lat=latitude,
            current_lng=longitude
        )


        return JsonResponse({"message": "Ambulance added successfully."}, status=201)

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "Failed to add ambulance", "error": str(e)}, status=400)

#end of adding ambulance api

# api to get all ambulances
@api_view(['GET'])
# @verify_firebase_token
def get_all_ambulances(request):
    try:
        ambulances = Ambulance.objects.all().order_by('-date_joined')

        ambulance_list = []
        for ambulance in ambulances:
            ambulance_list.append({
                "id": ambulance.id,
                "plate_number": ambulance.plate_number,
                "hospital": ambulance.hospital.hospital_name,
                "driver": ambulance.driver.full_name if ambulance.driver else "Unassigned",
                "latitude": ambulance.current_lat,
                "longitude": ambulance.current_lng,
                "status": ambulance.status,
                "date_joined": ambulance.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({
            "count": len(ambulance_list),
            "ambulances": ambulance_list
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to fetch ambulances", "error": str(e)},
            status=500
        )       

# end of get all ambulance api


# get nearest ambulance api
@api_view(["POST"])
# @verify_firebase_token
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


# delete user
@api_view(['DELETE'])
# @verify_firebase_token
def delete_ambulance(request):
    ambulance_id = request.data.get('ambulance_id')
    try:
        ambulance = Ambulance.objects.get(id=ambulance_id)

        if not ambulance:
            return Response({"error": "Ambulance not found"}, status=404)
        
        ambulance.delete()

        return Response({"message": "Ambulance deleted successfully"})
    except Ambulance.DoesNotExist:
        return Response({"error": "Ambulance not found"}, status=404)

# end of deleter user api


# Update ambulance status
@api_view(['PATCH'])
# @verify_firebase_token
def toggle_ambulance_status(request):
    ambulance_id = request.data.get('ambulance_id')
    status = request.data.get('status')
    try:
        ambulance = Ambulance.objects.get(id=ambulance_id)
        if not ambulance:
            return Response({"error": "Ambulance not found"}, status=404)

        ambulance.status = status
        ambulance.save()
        return Response({
            "message": "Status updated",
            "status": ambulance.status
        })
    except Ambulance.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of toggle ambulance api

# api to assign ambulance to driver
@api_view(['PATCH'])
# @verify_firebase_token
def assign_ambulance_to_driver(request):
    ambulance_id = request.data.get('ambulance_id')
    driver_id = request.data.get('driver_id')
    try:
        ambulance = Ambulance.objects.get(id=ambulance_id)
        driver = Driver.objects.get(id=driver_id)
        if not ambulance:
            return Response({"error": "Ambulance not found"}, status=404)
        if not driver:
            return Response({"error": "Driver not found"}, status=404)

        ambulance.driver = driver
        ambulance.save()
        return Response({
            "message": "Ambulance assigned to driver",
            "driver": driver.full_name
        })
    except Ambulance.DoesNotExist:
        return Response({"error": "Ambulance not found"}, status=404)
    except Driver.DoesNotExist:
        return Response({"error": "Driver not found"}, status=404)