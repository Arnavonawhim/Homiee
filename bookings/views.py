import math
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiParameter
from userdetails.models import Service, HelperProfile, ResidentProfile, HelperServicePrice
from bookings.models import Booking, Rating
from bookings import serializers

User = get_user_model()

_HELPER_CARD_EXAMPLE = {
    "helper_id": 12,
    "fname": "Ramesh",
    "lname": "Kumar",
    "username": "ramesh_k",
    "city": "Ghaziabad",
    "area": "Indirapuram",
    "profile_photo": "/media/helper_photos/2026/07/ramesh.jpg",
    "years_of_experience": 4,
    "avg_rating": "4.90",
    "rating_count": 37,
    "services": [
        {"service_id": 1, "name": "Cleaning", "slug": "cleaning", "price_per_hour": "150.00"},
        {"service_id": 3, "name": "Laundry", "slug": "laundry", "price_per_hour": "120.00"},
    ],
    "distance_km": 2.4,
}

_HELPER_DETAIL_EXAMPLE = {
    "helper_id": 12,
    "fname": "Ramesh",
    "lname": "Kumar",
    "username": "ramesh_k",
    "city": "Ghaziabad",
    "area": "Indirapuram",
    "profile_photo": "/media/helper_photos/2026/07/ramesh.jpg",
    "years_of_experience": 4,
    "avg_rating": "4.90",
    "rating_count": 37,
    "services": [
        {"service_id": 1, "name": "Cleaning", "slug": "cleaning", "price_per_hour": "150.00"},
    ],
    "distance_km": None,
    "about": "Experienced house cleaner available on weekdays.",
    "working_days": ["mon", "tue", "wed", "thu", "fri"],
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "ratings": [
        {"id": 8, "booking": 5, "resident": 3, "helper": 12, "score": 5, "feedback": "Excellent and punctual.", "created_at": "2026-07-08T11:20:00Z"},
    ],
}

_BOOKING_EXAMPLE = {
    "id": 5,
    "resident_id": 3,
    "resident_name": "Arnav Agrawal",
    "helper_id": 12,
    "helper_name": "Ramesh Kumar",
    "service_id": 1,
    "service": "Cleaning",
    "booking_date": "2026-06-12",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "special_instructions": "Please bring your own supplies.",
    "total_amount": "300.00",
    "status": "pending",
    "created_at": "2026-07-09T14:00:00Z",
    "updated_at": "2026-07-09T14:00:00Z",
}

_RATING_EXAMPLE = {
    "id": 8,
    "booking": 5,
    "resident": 3,
    "helper": 12,
    "score": 5,
    "feedback": "Excellent and punctual.",
    "created_at": "2026-07-09T15:30:00Z",
}


def _success_response(message, data, description, example_value):
    return OpenApiResponse(
        response=OpenApiTypes.OBJECT,
        description=description,
        examples=[OpenApiExample("Success", value={"status": "success", "message": message, "data": example_value})],
    )


_ERROR_400 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Validation error",
    examples=[
        OpenApiExample(
            "Validation Error",
            value={"status": "error", "message": "Validation failed.", "errors": {"field": ["This field is required."]}},
        )
    ],
)

_ERROR_401 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Authentication required",
    examples=[
        OpenApiExample(
            "Unauthorized",
            value={"status": "error", "message": "Authentication credentials were not provided."},
        )
    ],
)

_ERROR_403 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Permission denied",
    examples=[
        OpenApiExample(
            "Forbidden",
            value={"status": "error", "message": "You do not have access to this resource."},
        )
    ],
)

_ERROR_404 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Not found",
    examples=[
        OpenApiExample(
            "Not Found",
            value={"status": "error", "message": "Booking not found."},
        )
    ],
)


def _haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def _is_resident(user):
    return user.role in (User.Role.RESIDENT, User.Role.BOTH)


def _is_helper(user):
    return user.role in (User.Role.HELPER, User.Role.BOTH)


def _duration_hours(start_time, end_time):
    start = start_time.hour * 60 + start_time.minute
    end = end_time.hour * 60 + end_time.minute
    return (end - start) / 60.0


def _forbidden(message):
    return Response({"status": "error", "message": message}, status=status.HTTP_403_FORBIDDEN)


def _not_found(message):
    return Response({"status": "error", "message": message}, status=status.HTTP_404_NOT_FOUND)


def _bad_request(message):
    return Response({"status": "error", "message": message}, status=status.HTTP_400_BAD_REQUEST)


def _filter_by_service(queryset, service_param):
    if service_param.isdigit():
        return queryset.filter(services_offered__id=int(service_param)).distinct()
    return queryset.filter(services_offered__slug=service_param).distinct()


def _nearby_helpers(profile, radius_km, service_param):
    queryset = HelperProfile.objects.filter(city__iexact=profile.city).select_related("user").prefetch_related("service_prices__service")
    if service_param:
        queryset = _filter_by_service(queryset, service_param)
    distances = {}
    helpers = []
    for helper in queryset:
        if helper.latitude is None or helper.longitude is None:
            continue
        distance = _haversine_km(profile.latitude, profile.longitude, helper.latitude, helper.longitude)
        if distance <= radius_km:
            distances[helper.id] = distance
            helpers.append(helper)
    helpers.sort(key=lambda item: distances[item.id])
    return helpers, distances


class NearbyHelpersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("radius_km", OpenApiTypes.NUMBER, description="Search radius in kilometres. Defaults to 10."),
            OpenApiParameter("service", OpenApiTypes.STR, description="Optional service id or slug to filter by, e.g. 'cleaning'."),
        ],
        responses={
            200: _success_response("Nearby helpers fetched.", [_HELPER_CARD_EXAMPLE], "List of nearby helpers ordered by distance", [_HELPER_CARD_EXAMPLE]),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="Nearby helpers",
        description="Returns helpers in the resident's saved city within the given radius (computed from stored coordinates), ordered by distance.",
    )
    def get(self, request):
        if not _is_resident(request.user):
            return _forbidden("Only residents can view nearby helpers.")
        profile = ResidentProfile.objects.filter(user=request.user).first()
        if profile is None or not profile.city or profile.latitude is None or profile.longitude is None:
            return _bad_request("Add your address with city and coordinates to see nearby helpers.")
        try:
            radius_km = float(request.query_params.get("radius_km", 10))
        except (TypeError, ValueError):
            radius_km = 10.0
        helpers, distances = _nearby_helpers(profile, radius_km, request.query_params.get("service"))
        data = serializers.HelperCardSerializer(helpers, many=True, context={"distances": distances, "request": request}).data
        return Response({"status": "success", "message": "Nearby helpers fetched.", "data": data}, status=status.HTTP_200_OK)


class HelpersByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("service", OpenApiTypes.STR, required=True, description="Service id or slug of the quick category, e.g. 'cooking'."),
            OpenApiParameter("radius_km", OpenApiTypes.NUMBER, description="Search radius in kilometres. Defaults to 10."),
        ],
        responses={
            200: _success_response("Helpers fetched.", [_HELPER_CARD_EXAMPLE], "Helpers offering the selected category", [_HELPER_CARD_EXAMPLE]),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="Helpers by quick category",
        description="Returns nearby helpers (same city, within radius) who offer the selected service category.",
    )
    def get(self, request):
        if not _is_resident(request.user):
            return _forbidden("Only residents can view helpers by category.")
        service_param = request.query_params.get("service")
        if not service_param:
            return _bad_request("A service category is required.")
        profile = ResidentProfile.objects.filter(user=request.user).first()
        if profile is None or not profile.city or profile.latitude is None or profile.longitude is None:
            return _bad_request("Add your address with city and coordinates to see helpers.")
        try:
            radius_km = float(request.query_params.get("radius_km", 10))
        except (TypeError, ValueError):
            radius_km = 10.0
        helpers, distances = _nearby_helpers(profile, radius_km, service_param)
        data = serializers.HelperCardSerializer(helpers, many=True, context={"distances": distances, "request": request}).data
        return Response({"status": "success", "message": "Helpers fetched.", "data": data}, status=status.HTTP_200_OK)


class SearchHelpersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("q", OpenApiTypes.STR, description="Search text matched against first name, last name or service name.")],
        responses={
            200: _success_response("Search completed.", [_HELPER_CARD_EXAMPLE], "Helpers matching the search text", [_HELPER_CARD_EXAMPLE]),
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="Search helpers",
        description="Finds helpers by first name, last name or a service they offer, ordered by rating. Distance is null here as this search is not location bound.",
    )
    def get(self, request):
        if not _is_resident(request.user):
            return _forbidden("Only residents can search helpers.")
        query = request.query_params.get("q", "").strip()
        queryset = HelperProfile.objects.select_related("user").prefetch_related("service_prices__service")
        if query:
            queryset = queryset.filter(
                Q(user__fname__icontains=query) | Q(user__lname__icontains=query) | Q(services_offered__name__icontains=query)
            ).distinct()
        queryset = queryset.order_by("-avg_rating", "-rating_count")
        data = serializers.HelperCardSerializer(queryset, many=True, context={"request": request}).data
        return Response({"status": "success", "message": "Search completed.", "data": data}, status=status.HTTP_200_OK)


class HelperDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: _success_response("Helper fetched.", _HELPER_DETAIL_EXAMPLE, "Helper profile with services, availability and recent ratings", _HELPER_DETAIL_EXAMPLE),
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Helper detail",
        description="Returns a helper's services, pricing, availability and up to 20 recent ratings.",
    )
    def get(self, request, helper_id):
        if not _is_resident(request.user):
            return _forbidden("Only residents can view helper profiles.")
        profile = HelperProfile.objects.filter(user_id=helper_id).select_related("user").prefetch_related("service_prices__service").first()
        if profile is None:
            return _not_found("Helper not found.")
        data = serializers.HelperDetailSerializer(profile, context={"request": request}).data
        ratings = Rating.objects.filter(helper_id=helper_id).select_related("resident")[:20]
        data["ratings"] = serializers.RatingSerializer(ratings, many=True).data
        return Response({"status": "success", "message": "Helper fetched.", "data": data}, status=status.HTTP_200_OK)


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=serializers.BookingCreateSerializer,
        examples=[
            OpenApiExample(
                "Booking request",
                value={
                    "helper_id": 12,
                    "service_id": 1,
                    "booking_date": "2026-06-12",
                    "start_time": "10:00:00",
                    "end_time": "12:00:00",
                    "special_instructions": "Please bring your own supplies.",
                },
                request_only=True,
            )
        ],
        responses={
            201: _success_response("Booking request sent.", _BOOKING_EXAMPLE, "Booking created in pending status", _BOOKING_EXAMPLE),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="Create booking request",
        description="Residents create a booking for a helper. Total amount is calculated automatically as the helper's hourly price for the selected service multiplied by the booked hours.",
    )
    def post(self, request):
        if not _is_resident(request.user):
            return _forbidden("Only residents can create bookings.")
        serializer = serializers.BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        hours = _duration_hours(validated["start_time"], validated["end_time"])
        total_amount = (validated["price_per_hour"] * Decimal(str(hours))).quantize(Decimal("0.01"))
        booking = Booking.objects.create(
            resident=request.user,
            helper=validated["helper"],
            service=validated["service"],
            booking_date=validated["booking_date"],
            start_time=validated["start_time"],
            end_time=validated["end_time"],
            special_instructions=validated.get("special_instructions", ""),
            total_amount=total_amount,
        )
        data = serializers.BookingSerializer(booking).data
        return Response({"status": "success", "message": "Booking request sent.", "data": data}, status=status.HTTP_201_CREATED)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: _success_response("Booking fetched.", dict(_BOOKING_EXAMPLE, rating=None), "Booking detail visible only to the resident and the assigned helper", dict(_BOOKING_EXAMPLE, rating=None)),
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Booking detail",
        description="Returns a booking including special instructions. Only the resident who created it and the assigned helper can access it.",
    )
    def get(self, request, pk):
        booking = Booking.objects.select_related("resident", "helper", "service").filter(pk=pk).first()
        if booking is None:
            return _not_found("Booking not found.")
        if request.user.id not in (booking.resident_id, booking.helper_id):
            return _forbidden("You do not have access to this booking.")
        data = serializers.BookingSerializer(booking).data
        rating = Rating.objects.filter(booking=booking).first()
        data["rating"] = serializers.RatingSerializer(rating).data if rating else None
        return Response({"status": "success", "message": "Booking fetched.", "data": data}, status=status.HTTP_200_OK)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("status", OpenApiTypes.STR, description="Optional tab filter: pending, confirmed, completed, rejected or cancelled.")],
        responses={
            200: _success_response("Bookings fetched.", [_BOOKING_EXAMPLE], "Resident's bookings", [_BOOKING_EXAMPLE]),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="My bookings",
        description="Returns the logged-in resident's bookings, optionally filtered by status tab (pending / confirmed / completed).",
    )
    def get(self, request):
        if not _is_resident(request.user):
            return _forbidden("Only residents can view their bookings.")
        queryset = Booking.objects.filter(resident=request.user).select_related("helper", "service")
        status_param = request.query_params.get("status")
        if status_param:
            if status_param not in Booking.Status.values:
                return _bad_request("Invalid status filter.")
            queryset = queryset.filter(status=status_param)
        data = serializers.BookingSerializer(queryset, many=True).data
        return Response({"status": "success", "message": "Bookings fetched.", "data": data}, status=status.HTTP_200_OK)


class IncomingBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("status", OpenApiTypes.STR, description="Status filter or 'all'. Defaults to pending.")],
        responses={
            200: _success_response("Incoming requests fetched.", [dict(_BOOKING_EXAMPLE, resident_name="Arnav Agrawal")], "Booking requests assigned to the helper", [dict(_BOOKING_EXAMPLE, resident_name="Arnav Agrawal")]),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
        },
        tags=["Booking"],
        summary="Incoming requests",
        description="Returns bookings assigned to the logged-in helper. Defaults to pending requests; pass status=all to see every status.",
    )
    def get(self, request):
        if not _is_helper(request.user):
            return _forbidden("Only helpers can view incoming requests.")
        queryset = Booking.objects.filter(helper=request.user).select_related("resident", "service")
        status_param = request.query_params.get("status", Booking.Status.PENDING)
        if status_param and status_param != "all":
            if status_param not in Booking.Status.values:
                return _bad_request("Invalid status filter.")
            queryset = queryset.filter(status=status_param)
        data = serializers.BookingSerializer(queryset, many=True).data
        return Response({"status": "success", "message": "Incoming requests fetched.", "data": data}, status=status.HTTP_200_OK)


class BookingRespondView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=serializers.BookingRespondSerializer,
        examples=[
            OpenApiExample("Accept", value={"action": "accept"}, request_only=True),
            OpenApiExample("Reject", value={"action": "reject"}, request_only=True),
        ],
        responses={
            200: _success_response("Booking confirmed.", dict(_BOOKING_EXAMPLE, status="confirmed"), "Booking updated after the helper responds", dict(_BOOKING_EXAMPLE, status="confirmed")),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Accept or reject a request",
        description="The assigned helper accepts or rejects a pending booking request. Action must be 'accept' or 'reject'.",
    )
    def post(self, request, pk):
        booking = Booking.objects.filter(pk=pk).first()
        if booking is None:
            return _not_found("Booking not found.")
        if booking.helper_id != request.user.id:
            return _forbidden("Only the assigned helper can respond to this request.")
        if booking.status != Booking.Status.PENDING:
            return _bad_request("Only pending requests can be responded to.")
        serializer = serializers.BookingRespondSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        booking.status = Booking.Status.CONFIRMED if action == "accept" else Booking.Status.REJECTED
        booking.save(update_fields=["status", "updated_at"])
        data = serializers.BookingSerializer(booking).data
        return Response({"status": "success", "message": f"Booking {booking.status}.", "data": data}, status=status.HTTP_200_OK)


class CompleteBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: _success_response("Booking completed.", dict(_BOOKING_EXAMPLE, status="completed"), "Booking marked completed", dict(_BOOKING_EXAMPLE, status="completed")),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Mark booking complete",
        description="The resident marks a confirmed booking as completed. This unlocks rating. Send an empty request body.",
    )
    def post(self, request, pk):
        booking = Booking.objects.filter(pk=pk).first()
        if booking is None:
            return _not_found("Booking not found.")
        if booking.resident_id != request.user.id:
            return _forbidden("Only the resident who created this booking can complete it.")
        if booking.status != Booking.Status.CONFIRMED:
            return _bad_request("Only confirmed bookings can be marked complete.")
        booking.status = Booking.Status.COMPLETED
        booking.save(update_fields=["status", "updated_at"])
        data = serializers.BookingSerializer(booking).data
        return Response({"status": "success", "message": "Booking completed.", "data": data}, status=status.HTTP_200_OK)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: _success_response("Booking cancelled.", dict(_BOOKING_EXAMPLE, status="cancelled"), "Booking cancelled", dict(_BOOKING_EXAMPLE, status="cancelled")),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Cancel booking",
        description="The resident cancels a pending or confirmed booking. Send an empty request body.",
    )
    def post(self, request, pk):
        booking = Booking.objects.filter(pk=pk).first()
        if booking is None:
            return _not_found("Booking not found.")
        if booking.resident_id != request.user.id:
            return _forbidden("Only the resident who created this booking can cancel it.")
        if booking.status not in (Booking.Status.PENDING, Booking.Status.CONFIRMED):
            return _bad_request("This booking can no longer be cancelled.")
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        data = serializers.BookingSerializer(booking).data
        return Response({"status": "success", "message": "Booking cancelled.", "data": data}, status=status.HTTP_200_OK)


class RateHelperView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=serializers.RatingCreateSerializer,
        examples=[
            OpenApiExample(
                "Rating",
                value={"score": 5, "feedback": "Excellent and punctual."},
                request_only=True,
            )
        ],
        responses={
            201: _success_response("Rating submitted.", _RATING_EXAMPLE, "Rating stored and helper average recalculated", _RATING_EXAMPLE),
            400: _ERROR_400,
            401: _ERROR_401,
            403: _ERROR_403,
            404: _ERROR_404,
        },
        tags=["Booking"],
        summary="Rate a helper",
        description="The resident rates the helper for a completed booking (score 1-5, optional feedback). The helper's average rating and rating count are recalculated across all their ratings.",
    )
    def post(self, request, pk):
        booking = Booking.objects.select_related("helper").filter(pk=pk).first()
        if booking is None:
            return _not_found("Booking not found.")
        if booking.resident_id != request.user.id:
            return _forbidden("Only the resident who created this booking can rate it.")
        if booking.status != Booking.Status.COMPLETED:
            return _bad_request("You can only rate completed bookings.")
        if Rating.objects.filter(booking=booking).exists():
            return _bad_request("You have already rated this booking.")
        serializer = serializers.RatingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = Rating.objects.create(
            booking=booking,
            resident=request.user,
            helper=booking.helper,
            score=serializer.validated_data["score"],
            feedback=serializer.validated_data.get("feedback", ""),
        )
        aggregate = Rating.objects.filter(helper=booking.helper).aggregate(average=Avg("score"), count=Count("id"))
        profile = HelperProfile.objects.filter(user=booking.helper).first()
        if profile is not None:
            profile.avg_rating = round(aggregate["average"], 2)
            profile.rating_count = aggregate["count"]
            profile.save(update_fields=["avg_rating", "rating_count"])
        data = serializers.RatingSerializer(rating).data
        return Response({"status": "success", "message": "Rating submitted.", "data": data}, status=status.HTTP_201_CREATED)
