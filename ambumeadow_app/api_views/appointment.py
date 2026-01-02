import json
from rest_framework.decorators import api_view
from django.http import JsonResponse

from ambumeadow_app.models import User, Hospital, Staff, CareAppointment


@api_view(['POST'])
def schedule_care(request):
    try:
        data = json.loads(request.body)

        user_id = data.get("user_id")
        care_type = data.get("careType")
        hospital_id = data.get("hospital_id")
        doctor_id = data.get("doctor_id")
        date = data.get("date")
        time = data.get("time")
        notes = data.get("notes", "")

        # Validate required fields
        if not all([user_id, care_type, hospital_id, doctor_id, date, time]):
            return JsonResponse(
                {"message": "All required fields must be provided"},
                status=400
            )

        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"message": "User not found"}, status=404)

        hospital = Hospital.objects.filter(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"message": "Hospital not found"}, status=404)

        doctor = Staff.objects.filter(
            id=doctor_id,
            role='doctor',
            status='active'
        ).first()
        if not doctor:
            return JsonResponse(
                {"message": "Doctor not available"},
                status=404
            )

        appointment = CareAppointment.objects.create(
            user=user,
            care_type=care_type,
            hospital=hospital,
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            notes=notes
        )

        return JsonResponse({
            "message": "Appointment scheduled successfully",
            "appointment": {
                "id": appointment.id,
                "care_type": appointment.care_type,
                "hospital": hospital.hospital_name,
                "doctor": doctor.full_name,
                "date": str(appointment.appointment_date),
                "time": str(appointment.appointment_time),
                "status": appointment.status
            }
        }, status=201)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to schedule appointment", "error": str(e)},
            status=500
        )
