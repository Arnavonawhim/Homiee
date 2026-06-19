# profiles/serializers.py
from rest_framework import serializers
from userdetails.models import Service
from userdetails.serializers import ServiceSerializer,LanguageSerializer
from .models import ResidentProfile,HelperProfile,Language

class ResidentAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["house_no", "area", "city", "pincode", "latitude", "longitude"]


class ResidentServicesNeededSerializer(serializers.ModelSerializer):
    services_needed = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())

    class Meta:
        model = ResidentProfile
        fields = ["services_needed"]


class ResidentScheduleSerializer(serializers.ModelSerializer):
    preferred_time_slots = serializers.ListField(
        child=serializers.ChoiceField(choices=ResidentProfile.TimeSlot.choices)
    )
    days_required = serializers.ListField(
        child=serializers.ChoiceField(choices=ResidentProfile.Day.choices)
    )

    class Meta:
        model = ResidentProfile
        fields = ["work_type", "preferred_time_slots", "days_required"]


class ResidentSafetySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["emergency_contact_name", "emergency_contact_mobile"]


class ResidentProfileSerializer(serializers.ModelSerializer):
    services_needed = ServiceSerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, source="services_needed", queryset=Service.objects.all()
    )

    class Meta:
        model = ResidentProfile
        fields = [
            "house_no", "area", "city", "pincode", "latitude", "longitude",
            "services_needed", "service_ids",
            "work_type", "preferred_time_slots", "days_required",
            "emergency_contact_name", "emergency_contact_mobile",
        ]

class HelperServicesOfferedSerializer(serializers.ModelSerializer):
    services_offered = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())

    class Meta:
        model = HelperProfile
        fields = ["services_offered"]



class HelperExperienceSerializer(serializers.ModelSerializer):
    languages_spoken = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all())

    class Meta:
        model = HelperProfile
        fields = ["years_of_experience", "previous_work_reference", "languages_spoken"]



class HelperAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = [
            "work_preference", "working_hours", "areas_willing_to_work_in",
            "emergency_contact_name", "emergency_contact_mobile",
        ]


class HelperProfileSerializer(serializers.ModelSerializer):
    services_offered = ServiceSerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, source="services_offered", queryset=Service.objects.all()
    )
    languages_spoken = LanguageSerializer(many=True, read_only=True)
    language_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, source="languages_spoken", queryset=Language.objects.all()
    )

    class Meta:
        model = HelperProfile
        fields = [
            "services_offered", "service_ids",
            "years_of_experience", "previous_work_reference",
            "languages_spoken", "language_ids",
            "work_preference", "working_hours", "areas_willing_to_work_in",
            "emergency_contact_name", "emergency_contact_mobile",
        ]