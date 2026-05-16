from .common_imports import *


@api_view(['POST'])
def send_test_email(request):
    to_email = request.data.get("email")
    print("Sending test email to:", to_email)
    subject = "Test Email from Vitacura"
    html = "<h1>This is a test email from Ambumeadow</h1><p>If you received this, email sending works!</p>"

    try:
        send_email(to_email, subject, html)
        return JsonResponse({"message": "Test email sent successfully"})
    except Exception as e:
        return JsonResponse({"message": "Failed to send test email", "error": str(e)}, status=500)


# email verification and password reset token generation
# signup api
@api_view(['POST'])
def signup(request):
    try:
        data = request.data

        # username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}".strip()
        phone_number = data.get("phone_number")
        agreed = data.get("agreed")


        username = email

        if not all([email, password, full_name, phone_number]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)

        token = str(uuid.uuid4())

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            email_verification_token=token,
            email_verified=False,
            agreed=True,
        )

        link = f"http://192.168.100.12:8000/verify_email?token={token}"

        send_email(
            email,
            "Verify Your Vitacura Account",
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; color: #333;">
        
            <h2 style="color: #2563EB;">Welcome to Vitacura</h2>

            <p>
            Thank you for registering with Vitacura. To complete your account setup,
            please verify your email address by clicking the button below.
            </p>

            <div style="margin: 30px 0;">
            <a href="{link}" 
               style="
                    background-color: #2563EB;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    display: inline-block;
               ">
                Verify Email
            </a>
            </div>

            <p>
            If the button above does not work, copy and paste the link below into your browser:
            </p>

            <p style="word-break: break-all; color: #2563EB;">
            {link}
            </p>

            <hr style="margin: 30px 0;" />

            <p style="font-size: 14px; color: #777;">
            This verification link may expire after some time for security reasons.
            </p>

            <p style="font-size: 14px; color: #777;">
            Vitacura Team
            </p>
            </div>
            """
            )

        return JsonResponse({"message": "Account created successfully. Verify your email."}, status=201)

    except Exception as e:
        return JsonResponse({"message": "Signup failed", "error": str(e)}, status=500)

# email verification api
@api_view(['GET'])
def verify_email(request):
    token = request.GET.get("token")

    if not token:
        return render(request, "auth/email_result.html", {
            "status": "error",
            "title": "Invalid Request",
            "message": "Verification token is missing."
        })

    user = User.objects.filter(email_verification_token=token).first()

    if not user:
        return render(request, "auth/email_result.html", {
            "status": "error",
            "title": "Invalid Token",
            "message": "This verification link is invalid or has expired."
        })

    if user.email_verified:
        return render(request, "auth/email_result.html", {
            "status": "success",
            "title": "Already Verified",
            "message": "Your email is already verified."
        })

    user.email_verified = True
    user.email_verification_token = None
    user.save(update_fields=["email_verified", "email_verification_token"])

    return render(request, "auth/email_result.html", {
        "status": "success",
        "title": "Email Verified 🎉",
        "message": "Your account has been successfully verified. You can now log in."
    })


# sign in api
@api_view(['POST'])
def signin(request):
    try:
        username = request.data.get("email")
        password = request.data.get("password")

        print("Signin attempt:", {"username": username})

        if not username or not password:
            return JsonResponse({"message": "Username and password required"}, status=400)

        user = authenticate(request, username=username, password=password)

        if not user:
            return JsonResponse({"message": "Invalid credentials"}, status=401)

        if not user.email_verified:
            return JsonResponse({"message": "Verify your email first"}, status=403)

        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "user_id": user.id,
                "user_name": user.full_name,
                "user_email": user.email,
                "phone_number":user.phone_number,
                "phone_verified": user.phone_verified,
                "profile_image":user.profile_image,
                "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                "profile_image": user.profile_image,
            }
        })

    except Exception as e:
        return JsonResponse({"message": "Login failed", "error": str(e)}, status=500)


# password reset api
@api_view(['POST'])
def request_reset(request):
    email = request.data.get("email")

    user = User.objects.filter(email=email).first()
    if not user:
        return JsonResponse({"message": "User not found"}, status=404)

    token = str(uuid.uuid4())
    user.reset_token = token
    user.save()

    link = f"http://192.168.100.12:8000/reset_password?token={token}"

    send_email(
        email,
       "Reset Your Vitacura Password",
       f"""
       <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; color: #333;">

        <h2 style="color: #2563EB;">Password Reset Request</h2>

        <p>
            We received a request to reset your VinCab account password.
        </p>

        <p>
            Click the button below to create a new password:
        </p>

        <div style="margin: 30px 0;">
            <a href="{link}"
               style="
                    background-color: #DC2626;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    display: inline-block;
               ">
                Reset Password
            </a>
          </div>

          <p>
            If the button above does not work, copy and paste the link below into your browser:
          </p>

          <p style="word-break: break-all; color: #2563EB;">
            {link}
          </p>

          <hr style="margin: 30px 0;" />

          <p style="font-size: 14px; color: #777;">
            If you did not request a password reset, you can safely ignore this email.
          </p>

          <p style="font-size: 14px; color: #777;">
            For security reasons, this password reset link may expire after some time.
          </p>

          <p style="font-size: 14px; color: #777;">
            VinCab Team
          </p>

          </div>
          """
        )

    return JsonResponse({"message": "Email sent"})


# password reset api
@api_view(['GET', 'POST'])
def reset_password(request):
    token = request.GET.get("token") or request.data.get("token")

    if not token:
        return render(request, "auth/reset_result.html", {
            "status": "error",
            "message": "Missing reset token."
        })

    user = User.objects.filter(reset_token=token).first()

    if not user:
        return render(request, "auth/reset_result.html", {
            "status": "error",
            "message": "Invalid or expired reset link."
        })

    # -------------------
    # GET → show form
    # -------------------
    if request.method == "GET":
        return render(request, "auth/reset_password.html", {
            "token": token
        })

    # -------------------
    # POST → process form
    # -------------------
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    if not password or not confirm_password:
        return render(request, "auth/reset_password.html", {
            "token": token,
            "error": "All fields are required"
        })

    if password != confirm_password:
        return render(request, "auth/reset_password.html", {
            "token": token,
            "error": "Passwords do not match"
        })

    user.set_password(password)
    user.reset_token = None
    user.save(update_fields=["password", "reset_token"])

    return render(request, "auth/reset_result.html", {
        "status": "success",
        "message": "Password updated successfully. You can now log in."
    })


# refresh token api
@api_view(['POST'])
def refresh_token(request):
    try:
        refresh_token = request.data.get("refresh_token")

        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)

        return JsonResponse({
            "access_token": access_token
        })

    except Exception:
        return JsonResponse({"message": "Invalid refresh token"}, status=401)

# delete account api
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        user = request.user

        # Delete account
        user.delete()

        return JsonResponse({
            "message": "Account deleted successfully"
        }, status=200)

    except Exception as e:
        print("DELETE ACCOUNT ERROR:", str(e))

        return JsonResponse({
            "message": "Failed to delete account",
            "error": str(e)
        }, status=500)


# start of siginin for staffs
@api_view(['POST'])
def staff_signin(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        print("Staff signin attempt:", {"email": email})

        if not email or not password:
            return JsonResponse({
                "message": "Email and password required"
            }, status=400)

        # Authenticate User
        user = authenticate(
            request,
            username=email,
            password=password
        )

        if not user:
            return JsonResponse({
                "message": "Invalid credentials"
            }, status=401)

        # Check email verification
        if not user.email_verified:
            return JsonResponse({
                "message": "Verify your email first"
            }, status=403)

        # Check if user is staff
        if not hasattr(user, 'staff_profile'):
            return JsonResponse({
                "message": "Access denied. Not a staff account."
            }, status=403)

        staff = user.staff_profile

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "message": "Login successful",

            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),

            "staff": {
                "staff_id": staff.id,

                "user_id": user.id,

                "staff_name": user.full_name,

                "staff_email": user.email,

                "phone_number": user.phone_number,

                "department": staff.department,

                "role": staff.role,

                "status": staff.status,

                "phone_verified": user.phone_verified,

                "profile_image": (user.profile_image if user.profile_image else None),

                "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            }
        })

    except Exception as e:
        return JsonResponse({
            "message": "Login failed",
            "error": str(e)
        }, status=500)
# end of staff signin

# start of signup
@csrf_exempt
@api_view(['POST'])
def staff_signup(request):
    try:
        data = request.data

        full_name = data.get("full_name", "").strip()
        id_number = data.get("id_number")
        medical_license_number = data.get("medical_license_number")
        department = data.get("department")
        role = data.get("role")
        phone_number = data.get("phone_number")
        email = data.get("email")
        password = data.get("password")
        agreed = data.get("agreed")

        username = email

        # Validate required fields
        if not all([
            full_name,
            id_number,
            department,
            role,
            phone_number,
            email,
            password
        ]):
            return JsonResponse({
                "message": "Missing required fields"
            }, status=400)

        # Check existing user
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "message": "Username already exists"
            }, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "message": "Email already exists"
            }, status=400)

        if User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({
                "message": "Phone number already exists"
            }, status=400)

        # Generate verification token
        token = str(uuid.uuid4())

        # Create auth user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            agreed=agreed,
            email_verification_token=token,
            email_verified=False,
        )

        # Create staff profile
        staff = Staff.objects.create(
            user=user,
            id_number=id_number,
            medical_license_number=medical_license_number,
            department=department,
            role=role,
        )

        # Verification link
        link = f"http://192.168.100.12:8000/verify_email?token={token}"

        # Send verification email
        send_email(
            email,
            "Verify Your Vitacura Staff Account",
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; color: #333;">

            <h2 style="color: #2563EB;">Welcome to Vitacura Staff Portal</h2>

            <p>
            Your staff account has been created successfully.
            Please verify your email address to activate your account.
            </p>

            <div style="margin: 30px 0;">
                <a href="{link}"
                   style="
                        background-color: #2563EB;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        display: inline-block;
                   ">
                    Verify Email
                </a>
            </div>

            <p>
            If the button above does not work, copy and paste the link below into your browser:
            </p>

            <p style="word-break: break-all; color: #2563EB;">
            {link}
            </p>

            <hr style="margin: 30px 0;" />

            <p style="font-size: 14px; color: #777;">
            This verification link may expire after some time for security reasons.
            </p>

            <p style="font-size: 14px; color: #777;">
            Vitacura Team
            </p>

            </div>
            """
        )

        # Create welcome notification
        StaffNotification.objects.create(
            staff=staff,
            message="Welcome to Ambumeadow! Your staff account has been created successfully.",
            is_read=False
        )

        return JsonResponse({
            "message": "Staff account created successfully. Verify your email."
        }, status=201)

    except Exception as e:
        print(f"An error occurred: {e}")

        return JsonResponse({
            "message": "Staff signup failed",
            "error": str(e)
        }, status=500)
# end








# firebaseConfig = {
#   "apiKey": os.environ.get("FIREBASE_API_KEY"),
#   "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
#   "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
#   "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
#   "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
#   "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
#   "appId": os.environ.get("FIREBASE_APP_ID"),
#   "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID")
# };

# firebase = pyrebase.initialize_app(firebaseConfig)
# authe = firebase.auth() 
# database = firebase.database()

# # Initialize Firebase once (e.g., in settings.py or a startup file)
# # service_account_info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
# cred = credentials.Certificate("serviceAccountKey.json")
# # cred = credentials.Certificate(service_account_info)
# # firebase_admin.initialize_app(cred)s
# if not firebase_admin._apps:
#     firebase_admin.initialize_app(cred)

# # verify apis access
# def verify_firebase_token(view_func):
#     def wrapper(request, *args, **kwargs):
#         auth_header = request.headers.get("Authorization")

#         if not auth_header:
#             return JsonResponse({"error": "Authorization header missing"}, status=401)

#         try:
#             token = auth_header.split(" ")[1]  # "Bearer <token>"
#             decoded = auth.verify_id_token(token)
#             request.firebase_uid = decoded["uid"]   # <===== IMPORTANT
#         except Exception as e:
#             return JsonResponse({"error": "Invalid token", "details": str(e)}, status=401)

#         return view_func(request, *args, **kwargs)

#     return wrapper


# # api to refresh token
# @api_view(["POST"])
# def refresh_token(request):
#     refresh_token = request.data.get("refresh_token")

#     if not refresh_token:
#         return JsonResponse({"message": "Refresh token is required"}, status=400)

#     try:
#         # Pyrebase refresh
#         new_tokens = authe.refresh(refresh_token)

#         return JsonResponse({
#             "access_token": new_tokens["idToken"],
#             "refresh_token": new_tokens["refreshToken"],
#             "expires_in": new_tokens["expiresIn"],
#         })

#     except Exception as e:
#         return JsonResponse({
#             "message": "Failed to refresh token",
#             "error": str(e)
#         }, status=401)

# end


# # start of siginin
# @api_view(['POST'])
# def signin(request):
#     email = request.data.get("email")
#     password = request.data.get("password")

#     try:
#         # Try Firebase sign in
#         login = authe.sign_in_with_email_and_password(email, password)
#         id_token = login["idToken"]
#         refresh_token = login["refreshToken"]
#         expires_in = login["expiresIn"]

#         # Get account info
#         info = authe.get_account_info(id_token)
#         email_verified = info["users"][0]["emailVerified"]

#         if not email_verified:
#             # Resend verification email
#             authe.send_email_verification(id_token)

#             return JsonResponse({
#                 "message": "Email not verified. Verification link has been sent again."
#             }, status=403)

#         # Email verified → Continue login
#         uid = info["users"][0]["localId"]
#         db_user = User.objects.filter(firebase_uid=uid).first()
#         # log user action
#         # logger.info(f"User sign in: Email: {email}, Name: {db_user.full_name}")

#         return JsonResponse({
#             "message": "Login successful",
#             "access_token": id_token,
#             "refresh_token": refresh_token,
#             "expires_in": expires_in,
#             "user": {
#                 "user_id": db_user.id,
#                 "user_name": db_user.full_name,
#                 "user_email": db_user.email,
#                 "phone_number": db_user.phone_number,
#                 "phone_verified": db_user.phone_verified,
#                 "profile_image": db_user.profile_image.url if db_user.profile_image else None,
#                 "date_joined": db_user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
#             }
#         })

#     except Exception as e:
#         return JsonResponse({"message": "Invalid login", "error": str(e)}, status=401)
# # end

# # start of signup
# @csrf_exempt
# @api_view(['POST'])
# def signup(request):
#     data = request.data
#     first_name = data.get("first_name", "").strip()
#     last_name = data.get("last_name", "").strip()
#     full_name = f"{first_name} {last_name}".strip()
#     phone_number = data.get("phone_number")
#     email = data.get("email")
#     password = data.get("password")
#     agreed = data.get("agreed")

#     if not all([full_name, phone_number, email, password, agreed]):
#         return JsonResponse({"message": "Missing fields"}, status=400)

#     # check if email already exists in firebase
#     try:
#         existing_user = authe.get_user_by_email(email)
#         return JsonResponse({"message": "Email already exists"}, status=400)
#     except:
#         pass  # user does not exist, continue

#     try:
#         # Create user in Firebase
#         user = authe.create_user_with_email_and_password(email, password)

#         # # Send verification email
#         authe.send_email_verification(user['idToken'])

#         # # Save profile to Django database (NO PASSWORD)
#         uid = user["localId"]
#         User.objects.create(
#             firebase_uid=uid,
#             full_name=full_name,
#             phone_number=phone_number,
#             email=email,
#             agreed=agreed
#         )
#         # # log user action
#         # # logger.info(f"User sign up: Email: {email}, Name: {full_name}")

#         # # create welcome notification
#         db_user = User.objects.get(firebase_uid=uid)
#         Notification.objects.create(
#             user=db_user,
#             message="Welcome to Ambumeadow! Your account has been created successfully.",
#             is_read=False
#         )

#         return JsonResponse({"message": "Account created. Check your email to verify."}, status=201)

#     except Exception as e:
#         return JsonResponse({"message": "Signup failed", "error": str(e)}, status=400)
# # end

# start of siginin for staffs
# @api_view(['POST'])
# def staff_signin(request):
#     email = request.data.get("email")
#     password = request.data.get("password")

#     try:
#         # Try Firebase sign in
#         login = authe.sign_in_with_email_and_password(email, password)
#         id_token = login["idToken"]
#         refresh_token = login["refreshToken"]
#         expires_in = login["expiresIn"]

#         # Get account info
#         info = authe.get_account_info(id_token)
#         email_verified = info["users"][0]["emailVerified"]

#         if not email_verified:
#             # Resend verification email
#             authe.send_email_verification(id_token)

#             return JsonResponse({
#                 "message": "Email not verified. Verification link has been sent again."
#             }, status=403)

#         # Email verified → Continue login
#         uid = info["users"][0]["localId"]
#         db_staff = Staff.objects.filter(firebase_uid=uid).first()
#         # log user action
#         # logger.info(f"User sign in: Email: {email}, Name: {db_user.full_name}")

#         return JsonResponse({
#             "message": "Login successful",
#             "access_token": id_token,
#             "refresh_token": refresh_token,
#             "expires_in": expires_in,
#             "staff": {
#                 "staff_id": db_staff.id,
#                 "staff_name": db_staff.full_name,
#                 "staff_email": db_staff.email,
#                 "phone_number": db_staff.phone_number,
#                 "department": db_staff.department,
#                 "phone_verified": db_staff.phone_verified,
#                 "role": db_staff.role,
#                 "profile_image": db_staff.profile_image.url if db_staff.profile_image else None,
#                 "date_joined": db_staff.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
#             }
#         })

#     except Exception as e:
#         return JsonResponse({"message": "Invalid login", "error": str(e)}, status=401)
# # end of staff signin

# # start of signup
# @csrf_exempt
# @api_view(['POST'])
# def staff_signup(request):
#     data = request.data
#     full_name = data.get("full_name")
#     id_number = data.get("id_number")
#     medical_license_number = data.get("medical_license_number")
#     department = data.get("department")
#     role = data.get("role")
#     phone_number = data.get("phone_number")
#     email = data.get("email")
#     password = data.get("password")
#     agreed = data.get("agreed")

#     if not all([full_name, phone_number,id_number, medical_license_number, department, email, password, agreed]):
#         return JsonResponse({"message": "Missing fields"}, status=400)

#     # check if email already exists in firebase
#     try:
#         existing_user = authe.get_user_by_email(email)
#         return JsonResponse({"message": "Email already exists"}, status=400)
#     except:
#         pass  # user does not exist, continue

#     try:
#         # Create user in Firebase
#         user = authe.create_user_with_email_and_password(email, password)

#         # # Send verification email
#         authe.send_email_verification(user['idToken'])

#         # # Save profile to Django database (NO PASSWORD)
#         uid = user["localId"]
#         Staff.objects.create(
#             firebase_uid=uid,
#             full_name=full_name,
#             phone_number=phone_number,
#             id_number=id_number,
#             department=department,
#             medical_license_number=medical_license_number,
#             role=role,
#             email=email,
#             agreed=agreed
#         )
#         # # log user action
#         # # logger.info(f"User sign up: Email: {email}, Name: {full_name}")

#         # # create welcome notification
#         db_staff = Staff.objects.get(firebase_uid=uid)
#         StaffNotification.objects.create(
#             staff=db_staff,
#             message="Welcome to Ambumeadow! Your account has been created successfully.",
#             is_read=False
#         )

#         return JsonResponse({"message": "Account created. Check your email to verify."}, status=201)

#     except Exception as e:
#         return JsonResponse({"message": "Signup failed", "error": str(e)}, status=400)
# # end


# api to mark phone as verified
# @api_view(['POST'])
# @verify_firebase_token
# def verify_phone(request):
#     firebase_uid = request.firebase_uid

#     try:
#         user = User.objects.get(firebase_uid=firebase_uid)
#         user.phone_verified = True
#         user.save()

#         # send notification
#         Notification.objects.create(
#             user=user,
#             message="Phone number verified successfully.",
#             is_read=False
#         )

#         return JsonResponse({"message": "Phone number verified successfully"}, status=200)

#     except User.DoesNotExist:
#         return JsonResponse({"message": "User not found"}, status=404)
# end of phone verification api

# start of delete account api
# @api_view(['DELETE'])
# @verify_firebase_token
# def delete_account(request):
#     firebase_uid = request.firebase_uid

#     # 1. Delete from Firebase Auth
#     try:
#         auth.delete_user(firebase_uid)
#         print("Firebase user deleted")
#     except Exception as e:
#         print("Firebase delete error:", e)

#     # 2. Delete from Django database
#     user = User.objects.filter(firebase_uid=firebase_uid).first()
#     if user:
#         user.delete()

#     return JsonResponse({"message": "Account deleted successfully"}, status=200)
# # end

# # request password reset api
# @api_view(['POST'])
# def request_password_reset(request):
#     email = request.data.get("email")

#     try:
#         authe.send_password_reset_email(email)
#         return JsonResponse({"message": "Password reset email sent"})
#     except Exception as e:
#         return JsonResponse({"message": "Error sending reset email", "error": str(e)}, status=400)
# # end