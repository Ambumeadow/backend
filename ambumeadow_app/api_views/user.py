from .common_imports import *


# send expo_token -test api
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_expo_token(request, expo_token):
    send_push_notification(
        expo_token,
        "Test Notification",
        f"This is a test notification.",
        {"_id": 0}
    )
    return JsonResponse({"message":"Sent"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_notifications(request):
    try:
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-date')

        notification_list = []

        for notification in notifications:
            notification_list.append({
                "id": notification.id,
                "message": notification.message,
                "message_type": notification.message_type,
                "is_read": notification.is_read,
                "date": notification.date.strftime("%Y-%m-%d %H:%M:%S"),
            })

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return JsonResponse({
            "count": len(notification_list),
            "unread_count": unread_count,
            "notifications": notification_list,
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "message": "Failed to fetch notifications",
            "error": str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, doctor_id):
    messages = Chat.objects.filter(
        doctor_id=doctor_id,
        patient=request.user
    ).order_by('created_at')

    data = []

    for msg in messages:
        data.append({
            "id": msg.id,
            "text": msg.message,
            "sender": msg.sender_type,  # "patient" or "doctor"
            "created_at": msg.created_at
        })

    return Response({"messages": data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    doctor_id = request.data.get("doctor_id")
    message = request.data.get("message")

    chat = Chat.objects.create(
        doctor_id=doctor_id,
        patient=request.user,
        message=message,
        sender_type="patient"
    )

    return Response({"success": True})


# =========================================
# GET PATIENT SUMMARY
# =========================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_patient_summary(request):
    try:
        patient = Patient.objects.get(user=request.user)

        patient_data = {
            "id": patient.id,
            "full_name": patient.user.full_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "height": patient.height,
            "weight": patient.weight,
            "under_medication": patient.under_medication,
            "ward": patient.ward,
            "emergency_contact": patient.emergency_contact,
            "insurance_provider": patient.insurance_provider,
        }

        return Response({
            "success": True,
            "patient": patient_data
        })

    except Patient.DoesNotExist:
        return Response({
            "success": False,
            "message": "Patient profile not found"
        }, status=status.HTTP_404_NOT_FOUND)


# =========================================
# GET MEDICAL RECORDS
# =========================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_medical_records(request):
    try:
        patient = Patient.objects.get(user=request.user)

        records = MedicalRecord.objects.filter(
            patient=patient
        ).order_by("-date")

        records_data = []

        for record in records:
            records_data.append({
                "id": record.id,
                "patient_id": record.patient.id,
                "patient_name": record.patient.user.full_name,
                "doctor_name": record.doctor.user.full_name,
                "date": record.date,
                "diagnosis": record.diagnosis,
                "prescription": record.prescription,
                "notes": record.notes,
            })

        return Response({
            "success": True,
            "records": records_data
        })

    except Patient.DoesNotExist:
        return Response({
            "success": False,
            "message": "Patient not found"
        }, status=status.HTTP_404_NOT_FOUND)


# =========================================
# CREATE MEDICAL RECORD
# =========================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_medical_record(request):
    try:
        doctor = Staff.objects.get(user=request.user)

        patient_id = request.data.get("patient_id")
        diagnosis = request.data.get("diagnosis")
        prescription = request.data.get("prescription")
        notes = request.data.get("notes")

        patient = Patient.objects.get(id=patient_id)

        record = MedicalRecord.objects.create(
            patient=patient,
            doctor=doctor,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes,
        )

        return Response({
            "success": True,
            "message": "Medical record created",
            "record": {
                "id": record.id,
                "patient_name": patient.user.full_name,
                "doctor_name": doctor.user.full_name,
                "date": record.date,
                "diagnosis": record.diagnosis,
                "prescription": record.prescription,
                "notes": record.notes,
            }
        })

    except Staff.DoesNotExist:
        return Response({
            "success": False,
            "message": "Doctor profile not found"
        }, status=status.HTTP_403_FORBIDDEN)

    except Patient.DoesNotExist:
        return Response({
            "success": False,
            "message": "Patient not found"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)