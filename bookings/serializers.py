from django.contrib.auth import get_user_model
from rest_framework import serializers
from userdetails.models import Service, HelperProfile, HelperServicePrice
from bookings.models import Booking, Rating

User = get_user_model()


class HelperServiceInfoSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    name = serializers.CharField(source="service.name", read_only=True)
    slug = serializers.CharField(source="service.slug", read_only=True)

    class Meta:
        model = HelperServicePrice
        fields = ["service_id", "name", "slug", "price_per_hour"]


class HelperCardSerializer(serializers.ModelSerializer):
    helper_id = serializers.IntegerField(source="user.id", read_only=True)
    fname = serializers.CharField(source="user.fname", read_only=True)
    lname = serializers.CharField(source="user.lname", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    services = HelperServiceInfoSerializer(source="service_prices", many=True, read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = HelperProfile
        fields = [
            "helper_id", "fname", "lname", "username",
            "city", "area", "profile_photo", "years_of_experience",
            "avg_rating", "rating_count", "services", "distance_km",
        ]

    def validate(self, data):
        if data["avg_rating"]>5 or data["avg_rating"]<0:
            raise serializers.ValidationError({"avg_rating": "Rating must be between 0 and 5."})

    def get_distance_km(self, obj):
        distances = self.context.get("distances", {})
        value = distances.get(obj.id)
        return round(value, 2) if value is not None else None


class HelperDetailSerializer(HelperCardSerializer):
    class Meta(HelperCardSerializer.Meta):
        fields = HelperCardSerializer.Meta.fields + [
            "about", "working_days", "start_time", "end_time",
        ]


class BookingCreateSerializer(serializers.Serializer):
    helper_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    booking_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    special_instructions = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        helper = User.objects.filter(id=data["helper_id"], role__in=[User.Role.HELPER, User.Role.BOTH]).first()
        if helper is None:
            raise serializers.ValidationError({"helper_id": "Helper not found."})
        profile = HelperProfile.objects.filter(user=helper).first()
        if profile is None:
            raise serializers.ValidationError({"helper_id": "This helper has not completed their profile."})
        service = Service.objects.filter(id=data["service_id"]).first()
        if service is None:
            raise serializers.ValidationError({"service_id": "Service not found."})
        price = HelperServicePrice.objects.filter(helper=profile, service=service).first()
        if price is None:
            raise serializers.ValidationError({"service_id": "This helper does not offer the selected service."})
        data["helper"] = helper
        data["service"] = service
        data["price_per_hour"] = price.price_per_hour
        return data


class BookingRespondSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "reject"])


class RatingCreateSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "booking", "resident", "helper", "score", "feedback", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    resident_id = serializers.IntegerField(source="resident.id", read_only=True)
    helper_id = serializers.IntegerField(source="helper.id", read_only=True)
    resident_name = serializers.SerializerMethodField()
    helper_name = serializers.SerializerMethodField()
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    service = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "resident_id", "resident_name", "helper_id", "helper_name",
            "service_id", "service", "booking_date", "start_time", "end_time",
            "special_instructions", "total_amount", "status",
            "created_at", "updated_at",
        ]

    def get_resident_name(self, obj):
        return f"{obj.resident.fname} {obj.resident.lname}"

    def get_helper_name(self, obj):
        return f"{obj.helper.fname} {obj.helper.lname}"
