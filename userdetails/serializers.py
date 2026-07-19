import re
from rest_framework import serializers
from .models import Service, Language, ResidentProfile, HelperProfile, HelperServicePrice

def _normalize_mobile(value):
    digits = re.sub(r"\D", "", value or "")
    return digits[-10:] if len(digits) >= 10 else digits

def _validate_contact_mobile(serializer, value):
    normalized = _normalize_mobile(value)
    if len(normalized) != 10:
        raise serializers.ValidationError("Enter a valid 10-digit mobile number.")
    request = serializer.context.get("request")
    user = getattr(request, "user", None)
    if user is not None and user.mobile and _normalize_mobile(user.mobile) == normalized:
        raise serializers.ValidationError("You cannot use your own number as an emergency contact.")
    return normalized

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

class ResidentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ["profile_photo"]

class ResidentSOSRequestSerializer(serializers.Serializer):
    emergency_contact_name = serializers.CharField(max_length=100)
    emergency_contact_mobile = serializers.CharField(max_length=15)

    def validate_emergency_contact_mobile(self, value):
        return _validate_contact_mobile(self, value)

class HelperSOSRequestSerializer(serializers.Serializer):
    emergency_contact_name = serializers.CharField(max_length=100)
    emergency_contact_relation = serializers.CharField(max_length=50, required=False, allow_blank=True)
    emergency_contact_mobile = serializers.CharField(max_length=15)

    def validate_emergency_contact_mobile(self, value):
        return _validate_contact_mobile(self, value)

class SOSVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=6, max_length=6)

class ResidentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    fname = serializers.CharField(source="user.fname", read_only=True)
    lname = serializers.CharField(source="user.lname", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)

    class Meta:
        model = ResidentProfile
        fields = [
            "email", "fname", "lname", "mobile",
            "house_no", "area", "city", "pincode", "latitude", "longitude",
            "emergency_contact_name", "emergency_contact_mobile", "emergency_contact_verified",
            "profile_photo",
        ]

class HelperIdentitySerializer(serializers.ModelSerializer):
    back_card = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = HelperProfile
        fields = [
            "full_name", "date_of_birth", "govt_id_type", "govt_id_number",
            "front_card", "back_card","id_verified"
        ]

class HelperAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = ["house_no", "state", "city", "pincode", "latitude", "longitude"]

class HelperDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelperProfile
        fields = ["profile_photo", "police_verification_cert"]

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

class HelperProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    fname = serializers.CharField(source="user.fname", read_only=True)
    lname = serializers.CharField(source="user.lname", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)
    service_prices = HelperServicePriceReadSerializer(many=True, read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = HelperProfile
        fields = [
            "full_name", "email", "fname", "lname", "mobile",
            "date_of_birth", "govt_id_type", "govt_id_number",
            "front_card", "back_card",
            "house_no", "state", "city", "pincode", "latitude", "longitude",
            "profile_photo", "police_verification_cert",
            "service_prices",
            "years_of_experience", "languages_spoken", "about",
            "working_days", "start_time", "end_time",
            "emergency_contact_name", "emergency_contact_relation", "emergency_contact_mobile", "emergency_contact_verified",
        ]
