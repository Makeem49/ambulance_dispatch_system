from rest_framework import serializers
from ambulance_mgmt.models.ambulance import Ambulance, STATUS_CHOICES, TYPE_CHOICES
from hospital_mgmt.models import Hospital


class AmbulanceCreateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=STATUS_CHOICES.values)
    ambulance_type = serializers.ChoiceField(TYPE_CHOICES.values)
    hospital = serializers.PrimaryKeyRelatedField(queryset=Hospital.objects.all())

    class Meta:
        model = Ambulance
        fields = [
            "ambulance_registration_number",
            "latitude",
            "longitude",
            "status",
            "hospital",
            "ambulance_type",
        ]


class AmbulanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = "__all__"


class AmbulanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = fields = [
            "ambulance_registration_number",
            "latitude",
            "longitude",
            "status",
            "hospital",
            "ambulance_type",
        ]


class AmbulancePartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = ["latitude", "longitude", "status"]

    def __init__(self, instance=None, data=..., **kwargs):
        print("hello")
        super().__init__(instance, data, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        if latitude and not longitude:
            raise serializers.ValidationError(
                "Both latitude and longitude are require for location pin point."
            )

        if longitude and not latitude:
            raise serializers.ValidationError(
                "Both latitude and longitude are require for location pin point."
            )

        return super().validate(attrs)


class AmbulanceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = "__all__"
