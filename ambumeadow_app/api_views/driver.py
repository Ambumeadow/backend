import json
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from ambumeadow_app.models import Driver, Hospital, DriverNotification
from . auth import verify_firebase_token
from django.http import JsonResponse

from . auth import verify_firebase_token, authe



# start of driver signup
@csrf_exempt
@api_view(['POST'])
def driver_signup(request):
    data = request.data
    hospital_id = data.get("hospital_id")
    full_name = data.get("full_name")
    id_number = data.get("id_number")
    license_number = data.get("license_number")
    phone_number = data.get("phone_number")
    email = data.get("email")
    password = data.get("password")
    agreed = data.get("agreed")

    if not all([hospital_id, full_name, phone_number, id_number, license_number, email, password, agreed]):
        return JsonResponse({"message": "Missing fields"}, status=400)

    # check if email already exists in firebase
    try:
        existing_driver = authe.get_user_by_email(email)
        return JsonResponse({"message": "Email already exists"}, status=400)
    except:
        pass  # user does not exist, continue

    try:
        # Create user in Firebase
        driver = authe.create_user_with_email_and_password(email, password)

        # # Send verification email
        authe.send_email_verification(driver['idToken'])

        # # Save profile to Django database (NO PASSWORD)

        # check hosptal
        hospital = Hospital.objects.get(id=hospital_id)
        if not hospital:
            return JsonResponse({"message": "Hospital not found"}, status=404)

        uid = driver["localId"]
        Driver.objects.create(
            firebase_uid=uid,
            hospital=hospital,
            full_name=full_name,
            phone_number=phone_number,
            id_number=id_number,
            license_number=license_number,
            email=email,
            agreed=agreed
        )

        # # create welcome notification
        db_driver = Driver.objects.get(firebase_uid=uid)
        DriverNotification.objects.create(
            driver=db_driver,
            message="Welcome to Ambumeadow! Your account has been created successfully.",
            is_read=False
        )

        return JsonResponse({"message": "Account created. Check your email to verify."}, status=201)

    except Exception as e:
        return JsonResponse({"message": "Signup failed", "error": str(e)}, status=400)
# end

# api to get all drivers
@api_view(['GET'])
# @verify_firebase_token
def get_drivers(request, hospital_id):

    try:
        hospital = Hospital.objects.get(id=hospital_id)
        if not hospital:
            return JsonResponse({"message": "Hospital not found"}, status=404)

        # get all drivers
        drivers = Driver.objects.filter(hospital=hospital)

        # serialize drivers
        drivers_data = []
        for driver in drivers:
            drivers_data.append({
                "driver_id": driver.id,
                "driver_name": driver.full_name,
                "driver_email": driver.email,
                "phone_number": driver.phone_number,
                "license_number": driver.license_number,
                "id_number": driver.id_number,
                "profile_image": driver.profile_image.url if driver.profile_image else None,
                "date_joined": driver.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({"drivers": drivers_data}, status=200)

    except Driver.DoesNotExist:
        return JsonResponse({"message": "Driver not found"}, status=404)