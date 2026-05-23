from .common_imports import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_care(request):
    try:
        data = json.loads(request.body)

        user_id = data.get("user_id")
        care_type = data.get("careType")
        hospital_id = data.get("hospital_id")
        date = data.get("date")
        time = data.get("time")
        notes = data.get("notes", "")
        home_address = data.get("home_address", "")

        print("Data received for scheduling care:", user_id, care_type, hospital_id, date, time, notes, home_address)

        # Validate required fields
        if not all([user_id, care_type, hospital_id, date, home_address, time]):
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

        appointment = CareAppointment.objects.create(
            user=user,
            care_type=care_type,
            hospital=hospital,
            appointment_date=date,
            appointment_time=time,
            notes=notes,
            home_address=home_address,
            status='scheduled'
        )

        return JsonResponse({
            "message": "Appointment scheduled successfully",
            "appointment": {
                "id": appointment.id,
                "care_type": appointment.care_type,
                "hospital": hospital.hospital_name,
                "date": str(appointment.appointment_date),
                "time": str(appointment.appointment_time),
                "status": appointment.status
            }
        }, status=201)

    except Exception as e:
        print("Error scheduling care appointment:", str(e))
        return JsonResponse(
            {"message": "Failed to schedule appointment", "error": str(e)},
            status=500
        )


# api to get all appointments of the logged in user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_appointments(request):
    try:
        appointments = CareAppointment.objects.filter(
            user=request.user
        ).select_related(
            "hospital",
            "doctor",
            "doctor__user"
        ).order_by("-date_created")

        appointment_list = []

        for appointment in appointments:
            appointment_list.append({
                "id": appointment.id,
                "care_type": appointment.care_type,

                "hospital": {
                    "id": appointment.hospital.id,
                    "name": appointment.hospital.hospital_name,
                    "phone_number": appointment.hospital.phone_number,
                },

                "doctor": {
                    "id": appointment.doctor.id,
                    "name": appointment.doctor.user.full_name,
                    "department": appointment.doctor.department,
                    "phone_number": appointment.doctor.user.phone_number,
                } if appointment.doctor else None,

                "appointment_date": str(appointment.appointment_date),
                "appointment_time": str(appointment.appointment_time),

                "notes": appointment.notes,
                "home_address": appointment.home_address,

                "status": appointment.status,

                "date_created": appointment.date_created.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })

        return JsonResponse({
            "count": len(appointment_list),
            "appointments": appointment_list
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "message": "Failed to fetch appointments",
            "error": str(e)
        }, status=500)