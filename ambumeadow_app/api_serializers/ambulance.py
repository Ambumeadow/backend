from rest_framework import serializers
from ambumeadow_app.models import Ambulance


class NearestAmbulanceSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = Ambulance
        fields = [
            "id",
            "plate_number",
            "hospital",
            "driver",
            "current_lat",
            "current_lng",
            "distance_km",
        ]
