from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import pyrebase
import json

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes

from rest_framework.parsers import MultiPartParser, FormParser

from .. models import User, Notification, Staff, StaffNotification
from ..serializers import NotificationSerializer

import firebase_admin
from firebase_admin import credentials, auth

firebaseConfig = {
  "apiKey": os.environ.get("FIREBASE_API_KEY"),
  "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
  "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
  "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
  "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.environ.get("FIREBASE_APP_ID"),
  "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID")
};

firebase = pyrebase.initialize_app(firebaseConfig)
authe = firebase.auth() 
database = firebase.database()

# Initialize Firebase once (e.g., in settings.py or a startup file)
service_account_info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
# cred = credentials.Certificate("serviceAccountKey.json")
cred = credentials.Certificate(service_account_info)
# firebase_admin.initialize_app(cred)s
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# verify apis access
def verify_firebase_token(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        try:
            token = auth_header.split(" ")[1]  # "Bearer <token>"
            decoded = auth.verify_id_token(token)
            request.firebase_uid = decoded["uid"]   # <===== IMPORTANT
        except Exception as e:
            return JsonResponse({"error": "Invalid token", "details": str(e)}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


# start of siginin
@api_view(['POST'])
def signin(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        # Try Firebase sign in
        login = authe.sign_in_with_email_and_password(email, password)
        id_token = login["idToken"]

        # Get account info
        info = authe.get_account_info(id_token)
        email_verified = info["users"][0]["emailVerified"]

        if not email_verified:
            # Resend verification email
            authe.send_email_verification(id_token)

            return JsonResponse({
                "message": "Email not verified. Verification link has been sent again."
            }, status=403)

        # Email verified → Continue login
        uid = info["users"][0]["localId"]
        db_user = User.objects.filter(firebase_uid=uid).first()
        # log user action
        # logger.info(f"User sign in: Email: {email}, Name: {db_user.full_name}")

        return JsonResponse({
            "message": "Login successful",
            "access_token": id_token,
            "user": {
                "user_id": db_user.id,
                "user_name": db_user.full_name,
                "user_email": db_user.email,
                "phone_number": db_user.phone_number,
                "phone_verified": db_user.phone_verified,
                "profile_image": db_user.profile_image.url if db_user.profile_image else None,
                "date_joined": db_user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            }
        })

    except Exception as e:
        return JsonResponse({"message": "Invalid login", "error": str(e)}, status=401)
# end

# start of signup
@csrf_exempt
@api_view(['POST'])
def signup(request):
    data = request.data
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    full_name = f"{first_name} {last_name}".strip()
    phone_number = data.get("phone_number")
    email = data.get("email")
    password = data.get("password")
    agreed = data.get("agreed")

    if not all([full_name, phone_number, email, password, agreed]):
        return JsonResponse({"message": "Missing fields"}, status=400)

    # check if email already exists in firebase
    try:
        existing_user = authe.get_user_by_email(email)
        return JsonResponse({"message": "Email already exists"}, status=400)
    except:
        pass  # user does not exist, continue

    try:
        # Create user in Firebase
        user = authe.create_user_with_email_and_password(email, password)

        # # Send verification email
        authe.send_email_verification(user['idToken'])

        # # Save profile to Django database (NO PASSWORD)
        uid = user["localId"]
        User.objects.create(
            firebase_uid=uid,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            agreed=agreed
        )
        # # log user action
        # # logger.info(f"User sign up: Email: {email}, Name: {full_name}")

        # # create welcome notification
        db_user = User.objects.get(firebase_uid=uid)
        Notification.objects.create(
            user=db_user,
            message="Welcome to Ambumeadow! Your account has been created successfully.",
            is_read=False
        )

        return JsonResponse({"message": "Account created. Check your email to verify."}, status=201)

    except Exception as e:
        return JsonResponse({"message": "Signup failed", "error": str(e)}, status=400)
# end

# start of siginin for staffs
@api_view(['POST'])
def staff_signin(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        # Try Firebase sign in
        login = authe.sign_in_with_email_and_password(email, password)
        id_token = login["idToken"]

        # Get account info
        info = authe.get_account_info(id_token)
        email_verified = info["users"][0]["emailVerified"]

        if not email_verified:
            # Resend verification email
            authe.send_email_verification(id_token)

            return JsonResponse({
                "message": "Email not verified. Verification link has been sent again."
            }, status=403)

        # Email verified → Continue login
        uid = info["users"][0]["localId"]
        db_staff = Staff.objects.filter(firebase_uid=uid).first()
        # log user action
        # logger.info(f"User sign in: Email: {email}, Name: {db_user.full_name}")

        return JsonResponse({
            "message": "Login successful",
            "access_token": id_token,
            "staff": {
                "staff_id": db_staff.id,
                "staff_name": db_staff.full_name,
                "staff_email": db_staff.email,
                "phone_number": db_staff.phone_number,
                "department": db_staff.department,
                "phone_verified": db_staff.phone_verified,
                "role": db_staff.role,
                "profile_image": db_staff.profile_image.url if db_staff.profile_image else None,
                "date_joined": db_staff.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            }
        })

    except Exception as e:
        return JsonResponse({"message": "Invalid login", "error": str(e)}, status=401)
# end of staff signin

# start of signup
@csrf_exempt
@api_view(['POST'])
def staff_signup(request):
    data = request.data
    full_name = data.get("full_name")
    id_number = data.get("id_number")
    medical_license_number = data.get("medical_license_number")
    department = data.get("department")
    role = data.get("role")
    phone_number = data.get("phone_number")
    email = data.get("email")
    password = data.get("password")
    agreed = data.get("agreed")

    if not all([full_name, phone_number,id_number, medical_license_number, department, email, password, agreed]):
        return JsonResponse({"message": "Missing fields"}, status=400)

    # check if email already exists in firebase
    try:
        existing_user = authe.get_user_by_email(email)
        return JsonResponse({"message": "Email already exists"}, status=400)
    except:
        pass  # user does not exist, continue

    try:
        # Create user in Firebase
        user = authe.create_user_with_email_and_password(email, password)

        # # Send verification email
        authe.send_email_verification(user['idToken'])

        # # Save profile to Django database (NO PASSWORD)
        uid = user["localId"]
        Staff.objects.create(
            firebase_uid=uid,
            full_name=full_name,
            phone_number=phone_number,
            id_number=id_number,
            role=role,
            email=email,
            agreed=agreed
        )
        # # log user action
        # # logger.info(f"User sign up: Email: {email}, Name: {full_name}")

        # # create welcome notification
        db_staff = Staff.objects.get(firebase_uid=uid)
        StaffNotification.objects.create(
            staff=db_staff,
            message="Welcome to Ambumeadow! Your account has been created successfully.",
            is_read=False
        )

        return JsonResponse({"message": "Account created. Check your email to verify."}, status=201)

    except Exception as e:
        return JsonResponse({"message": "Signup failed", "error": str(e)}, status=400)
# end


# api to mark phone as verified
@api_view(['POST'])
@verify_firebase_token
def verify_phone(request):
    firebase_uid = request.firebase_uid

    try:
        user = User.objects.get(firebase_uid=firebase_uid)
        user.phone_verified = True
        user.save()

        # send notification
        Notification.objects.create(
            user=user,
            message="Phone number verified successfully.",
            is_read=False
        )

        return JsonResponse({"message": "Phone number verified successfully"}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404)
# end of phone verification api

# start of delete account api
@api_view(['DELETE'])
@verify_firebase_token
def delete_account(request):
    firebase_uid = request.firebase_uid

    # 1. Delete from Firebase Auth
    try:
        auth.delete_user(firebase_uid)
        print("Firebase user deleted")
    except Exception as e:
        print("Firebase delete error:", e)

    # 2. Delete from Django database
    user = User.objects.filter(firebase_uid=firebase_uid).first()
    if user:
        user.delete()

    return JsonResponse({"message": "Account deleted successfully"}, status=200)
# end

# request password reset api
@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get("email")

    try:
        authe.send_password_reset_email(email)
        return JsonResponse({"message": "Password reset email sent"})
    except Exception as e:
        return JsonResponse({"message": "Error sending reset email", "error": str(e)}, status=400)
# end