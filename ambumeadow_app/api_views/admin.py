from .common_imports import *

# api to get all users
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    users = User.objects.all()

    user_data = []

    for user in users:
        user_data.append({
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
        })

    return JsonResponse({
        "total_users": users.count(),
        "users": user_data
    })
# end of get all users api


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_doctors(request):
    doctors = Staff.objects.filter(role="doctor")

    doctor_data = []

    for doctor in doctors:
        doctor_data.append({
            "id": doctor.id,
            "full_name": doctor.user.full_name,
            "phone_number": doctor.user.phone_number,
            "email": doctor.user.email,
            "is_active": doctor.status,
            "hospital": doctor.hospital.hospital_name,
            "department": doctor.department,
            "date_joined": doctor.date_joined,
        })

    return JsonResponse({
        "total_doctors": doctors.count(),
        "doctors": doctor_data
    })
# end of get all doctors api


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_nurses(request):
    nurses = Staff.objects.filter(role="nurse")

    nurse_data = []

    for nurse in nurses:
        nurse_data.append({
            "id": nurse.id,
            "full_name": nurse.user.full_name,
            "phone_number": nurse.user.phone_number,
            "email": nurse.user.email,
            "is_active": nurse.status,
            "hospital": nurse.hospital.hospital_name,
            "department": nurse.department,
            "date_joined": nurse.date_joined,
        })

    return JsonResponse({
        "total_nurses": nurses.count(),
        "nurses": nurse_data
    })
# end of get all nurses api



@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_all_appointments(request):
    appointments = CareAppointment.objects.select_related('user','hospital','doctor').all().order_by('-date_created')

    appointment_data = []

    for appointment in appointments:
        appointment_data.append({
            "id": appointment.id,
            "patient_name": appointment.user.full_name,
            "phone_number": appointment.user.phone_number,
            "hospital": appointment.hospital.hospital_name,
            "doctor": appointment.doctor.user.full_name if appointment.doctor else None,
            "care_type": appointment.care_type,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "notes": appointment.notes,
            "home_address": appointment.home_address,
            "status": appointment.status,
            "date_created": appointment.date_created,
        })

    return JsonResponse({
        "total_appointments": appointments.count(),
        "appointments": appointment_data
    })
# end of get all appointments api



# start of get all payments
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_all_payments(request):
    payments = Payment.objects.select_related(
        'user',
        'hospital'
    ).all().order_by('-paid_at')

    payment_data = []

    for payment in payments:
        payment_data.append({
            "id": payment.id,
            "patient_name": payment.user.full_name,
            "phone_number": payment.user.phone_number,
            "hospital": payment.hospital.hospital_name,
            "service_type": payment.service_type,
            "amount": float(payment.amount),
            "method": payment.method,
            "receipt_number": payment.receipt_number,
            "transaction_reference": payment.transaction_reference,
            "status": payment.status,
            "paid_at": payment.paid_at,
        })

    total_revenue = (
        Payment.objects
        .filter(status='paid')
        .aggregate(total=Sum('amount'))['total']
        or 0
    )

    return JsonResponse({
        "total_payments": payments.count(),
        "successful_payments": payments.filter(status='paid').count(),
        "pending_payments": payments.filter(status='pending').count(),
        "failed_payments": payments.filter(status='failed').count(),
        "total_revenue": float(total_revenue),
        "payments": payment_data,
    })
# end of get all payments


# delete user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)

        if not user:
            return Response({"error": "User not found"}, status=404)

        # delete user in firebase
        firebase_uid = user.firebase_uid
        if firebase_uid:
            auth.delete_user(firebase_uid)
        
        user.delete()

        return Response({"message": "User deleted successfully"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of deleter user api


# Activate / Suspend user
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_user_status(request):
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return Response({"error": "User not found"}, status=404)

        user.is_active = not user.is_active
        user.save()
        return Response({
            "message": "Status updated",
            "is_active": user.is_active
        })
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

# end of toggle user api