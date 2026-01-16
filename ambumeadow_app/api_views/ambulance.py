import json
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from ambumeadow_app.models import Hospital, Ambulance, AmbulanceBooking, Payment, User
from . auth import verify_firebase_token
from django.http import JsonResponse

from . auth import verify_firebase_token

from ambumeadow_app.api_serializers.ambulance import NearestAmbulanceSerializer
from ambumeadow_app.utils.distance import haversine
from ambumeadow_app.utils.verify_paystack import verify_paystack_payment

import requests
from django.conf import settings
from django.utils import timezone

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
        "latitude": -1.2921,
        "longitude": 36.8219
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

    AVERAGE_SPEED_KMH = 50  # You can change this (city traffic)

    results = []

    for ambulance in ambulances:
        distance = haversine(
            float(lat),
            float(lng),
            ambulance.current_lat,
            ambulance.current_lng,
        )

        distance_km = round(distance, 2)

        # 🕒 ETA in minutes
        eta_minutes = round((distance_km / AVERAGE_SPEED_KMH) * 60)

        ambulance.distance_km = distance_km
        ambulance.eta_minutes = eta_minutes

        results.append(ambulance)

    # sort by nearest
    results.sort(key=lambda x: x.distance_km)

    serializer = NearestAmbulanceSerializer(results, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



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


# api to book ambulance
@api_view(["POST"])
# @verify_firebase_token
@csrf_exempt
def book_ambulance(request):
    user_id = request.data.get("user_id")
    ambulance_id = request.data.get("ambulance_id")
    reference = request.data.get("payment_reference")
    amount = request.data.get("amount")
    pickup_lat = request.data.get("pickup_latitude")
    pickup_lng = request.data.get("pickup_longitude")

    if not all([ambulance_id, reference, amount, pickup_lat, pickup_lng]):
        return Response({"error": "Missing fields"}, status=400)

    # ================= CHECK AMBULANCE =================
    try:
        ambulance = Ambulance.objects.get(id=ambulance_id)
    except Ambulance.DoesNotExist:
        return Response({"error": "Ambulance not found"}, status=404)

    if ambulance.status != "available":
        return Response({"error": "Ambulance is not available"}, status=400)

    # ================= VERIFY PAYMENT =================
    paystack_response = verify_paystack_payment(reference)

    if not paystack_response.get("status"):
        return Response({"error": "Payment verification failed"}, status=400)

    data = paystack_response.get("data")

    if data["status"] != "success":
        return Response({"error": "Payment not successful"}, status=400)

    paid_amount = data["amount"] / 100  # convert from kobo/cents

    if float(paid_amount) != float(amount):
        return Response({"error": "Amount mismatch"}, status=400)

    # check user
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=404)

    # ================= SAVE PAYMENT =================
    payment = Payment.objects.create(
        user=user,
        hospital=ambulance.hospital,
        service_type="ambulance_booking",
        amount=amount,
        method="paystack",
        transaction_reference=reference,
        receipt_number=data.get("reference"),
        status="paid",
        paid_at=timezone.now(),
    )

    # ================= CREATE BOOKING =================
    booking = AmbulanceBooking.objects.create(
        user=user,
        ambulance=ambulance,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lng,
    )

    # ================= LOCK AMBULANCE =================
    ambulance.status = "busy"
    ambulance.is_available = False
    ambulance.save()

    return Response({
        "message": "Ambulance booked successfully",
        "booking_id": booking.id,
        "payment_id": payment.id,
    }, status=201)
