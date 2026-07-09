from rest_framework import serializers
from .models import Service, Language, ResidentProfile, HelperProfile, HelperServicePrice

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "slug"]

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code"]

class ResidentAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["house_no", "area", "city", "pincode", "latitude", "longitude"]

class ResidentEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["emergency_contact_name", "emergency_contact_mobile"]

class ResidentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["profile_photo"]

class ResidentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = [
            "house_no", "area", "city", "pincode", "latitude", "longitude",
            "emergency_contact_name", "emergency_contact_mobile",
            "profile_photo",
        ]

class HelperIdentitySerializer(serializers.ModelSerializer):
    pan_card = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = HelperProfile
        fields = [
            "full_name", "date_of_birth", "govt_id_type", "govt_id_number",
            "aadhaar_card", "pan_card",
        ]

class HelperAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = ["house_no", "area", "city", "pincode", "latitude", "longitude"]

class HelperDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = ["profile_photo", "police_verification_cert", "address_proof"]

class HelperServicePriceSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    class Meta:
        model = HelperServicePrice
        fields = ["service", "price_per_hour"]
class HelperServicePriceReadSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    class Meta:
        model = HelperServicePrice
        fields = ["service", "price_per_hour"]

class HelperServicesPricingSerializer(serializers.ModelSerializer):
    service_prices = HelperServicePriceSerializer(many=True)
    class Meta:
        model = HelperProfile
        fields = ["service_prices"]
    def update(self, instance, validated_data):
        service_prices = validated_data.pop("service_prices", None)
        if service_prices is not None:
            instance.service_prices.all().delete()
            for item in service_prices:
                HelperServicePrice.objects.create(
                    helper=instance,
                    service=item["service"],
                    price_per_hour=item["price_per_hour"],
                )
        return instance
class HelperExperienceSerializer(serializers.ModelSerializer):
    languages_spoken = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all())
    class Meta:
        model = HelperProfile
        fields = ["years_of_experience", "languages_spoken", "about"]
class HelperAvailabilitySerializer(serializers.ModelSerializer):
    working_days = serializers.ListField(
        child=serializers.ChoiceField(choices=HelperProfile.Day.choices)
    )
    class Meta:
        model = HelperProfile
        fields = ["working_days", "start_time", "end_time"]
class HelperEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = ["emergency_contact_name", "emergency_contact_relation", "emergency_contact_mobile"]

class HelperProfileSerializer(serializers.ModelSerializer):
    service_prices = HelperServicePriceReadSerializer(many=True, read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = HelperProfile
        fields = [
            "full_name", "date_of_birth", "govt_id_type", "govt_id_number",
            "aadhaar_card", "pan_card",
            "house_no", "area", "city", "pincode", "latitude", "longitude",
            "profile_photo", "police_verification_cert", "address_proof",
            "service_prices",
            "years_of_experience", "languages_spoken", "about",
            "working_days", "start_time", "end_time",
            "emergency_contact_name", "emergency_contact_relation", "emergency_contact_mobile",
        ]
