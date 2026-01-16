from rest_framework import serializers
from ambumeadow_app.models import Ambulance


class NearestAmbulanceSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True)
    eta_minutes = serializers.IntegerField(read_only=True)
    hospital_name = serializers.CharField(source="hospital.hospital_name", read_only=True)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True)

    class Meta:
        model = Ambulance
        fields = [
            "id",
            "plate_number",
            "hospital_name",
            "driver_name",
            "current_lat",
            "current_lng",
            "distance_km",
            "eta_minutes",
            "status",
        ]
