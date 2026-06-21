from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiTypes
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ResidentProfile, HelperProfile
from .serializers import (
    ResidentAddressSerializer,
    ResidentServicesNeededSerializer,
    ResidentScheduleSerializer,
    ResidentSafetySerializer,
    ResidentProfileSerializer,
    HelperServicesOfferedSerializer,
    HelperExperienceSerializer,
    HelperAvailabilitySerializer,
    HelperProfileSerializer,
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


class ResidentProfileStepMixin:
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = ResidentProfile.objects.get_or_create(user=self.request.user)
        return profile

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        request=ResidentAddressSerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentAddressSerializer,
                description="Address saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"house_no": "12A", "area": "Indirapuram", "city": "Ghaziabad", "pincode": "201014"},
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident — address (step 1)",
        description="Creates the resident profile if it doesn't exist yet and saves the address fields.",
    )
)
class ResidentAddressView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentAddressSerializer


@extend_schema_view(
    post=extend_schema(
        request=ResidentServicesNeededSerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentServicesNeededSerializer,
                description="Services needed saved",
                examples=[OpenApiExample("Success", value={"services_needed": [1, 3]})],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident — type of help needed (step 2)",
        description="Sets the list of Service IDs the resident needs help with.",
    )
)
class ResidentServicesNeededView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentServicesNeededSerializer


@extend_schema_view(
    post=extend_schema(
        request=ResidentScheduleSerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentScheduleSerializer,
                description="Schedule saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "work_type": "Part-time",
                            "preferred_time_slots": ["morning", "evening"],
                            "days_required": ["mon", "wed", "fri"],
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident — schedule (step 3)",
        description="Sets work type, preferred time slots, and the days help is required.",
    )
)
class ResidentScheduleView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentScheduleSerializer


@extend_schema_view(
    post=extend_schema(
        request=ResidentSafetySerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentSafetySerializer,
                description="Emergency contact saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"emergency_contact_name": "Ramesh Kumar", "emergency_contact_mobile": "9876543210"},
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident — safety & identity (step 4)",
        description="Sets the emergency contact name and mobile number.",
    )
)
class ResidentSafetyView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentSafetySerializer


@extend_schema_view(
    get=extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=ResidentProfileSerializer,
                description="Full resident profile",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "house_no": "12A",
                            "area": "Indirapuram",
                            "city": "Ghaziabad",
                            "pincode": "201014",
                            "services_needed": [
                                {"id": 1, "name": "House cleaning", "slug": "house-cleaning"},
                                {"id": 3, "name": "Cooking", "slug": "cooking"},
                            ],
                            "work_type": "Part-time",
                            "preferred_time_slots": ["morning", "evening"],
                            "days_required": ["mon", "wed", "fri"],
                            "emergency_contact_name": "Ramesh Kumar",
                            "emergency_contact_mobile": "9876543210",
                        },
                    )
                ],
            ),
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident — full profile",
        description="Returns every onboarding step combined for the logged-in resident.",
    )
)
class ResidentProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ResidentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = ResidentProfile.objects.get_or_create(user=self.request.user)
        return profile


class HelperProfileStepMixin:
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = HelperProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"years_of_experience": 0},
        )
        return profile

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        request=HelperServicesOfferedSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperServicesOfferedSerializer,
                description="Services offered saved",
                examples=[OpenApiExample("Success", value={"services_offered": [2, 4]})],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper — services offered (step 1)",
        description="Sets the list of Service IDs the helper offers.",
    )
)
class HelperServicesOfferedView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperServicesOfferedSerializer


@extend_schema_view(
    post=extend_schema(
        request=HelperExperienceSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperExperienceSerializer,
                description="Experience & skills saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "years_of_experience": 3,
                            "previous_work_reference": "Worked with Sharma family for 2 years",
                            "languages_spoken": [1, 2],
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper — experience & skills (step 2)",
        description="Sets years of experience, an optional reference, and Language IDs spoken.",
    )
)
class HelperExperienceView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperExperienceSerializer


@extend_schema_view(
    post=extend_schema(
        request=HelperAvailabilitySerializer,
        responses={
            200: OpenApiResponse(
                response=HelperAvailabilitySerializer,
                description="Availability & trust info saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "work_preference": "Full-time",
                            "working_hours": "9 AM - 6 PM",
                            "areas_willing_to_work_in": "Indirapuram, Vaishali",
                            "emergency_contact_name": "Sunita Devi",
                            "emergency_contact_mobile": "9123456780",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper — availability & trust (step 3)",
        description="Sets work preference, working hours, areas willing to work in, and emergency contact.",
    )
)
class HelperAvailabilityView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperAvailabilitySerializer


@extend_schema_view(
    get=extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=HelperProfileSerializer,
                description="Full helper profile",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "services_offered": [
                                {"id": 2, "name": "Cooking", "slug": "cooking"},
                                {"id": 4, "name": "Babysitting", "slug": "babysitting"},
                            ],
                            "years_of_experience": 3,
                            "previous_work_reference": "Worked with Sharma family for 2 years",
                            "languages_spoken": [
                                {"id": 1, "name": "English", "code": "en"},
                                {"id": 2, "name": "Hindi", "code": "hi"},
                            ],
                            "work_preference": "Full-time",
                            "working_hours": "9 AM - 6 PM",
                            "areas_willing_to_work_in": "Indirapuram, Vaishali",
                            "emergency_contact_name": "Sunita Devi",
                            "emergency_contact_mobile": "9123456780",
                        },
                    )
                ],
            ),
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper — full profile",
        description="Returns every onboarding step combined for the logged-in helper.",
    )
)
class HelperProfileDetailView(generics.RetrieveAPIView):
    serializer_class = HelperProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = HelperProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"years_of_experience": 0},
        )
        return profile