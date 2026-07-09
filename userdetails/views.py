from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiTypes
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ResidentProfile, HelperProfile
from .serializers import (ResidentAddressSerializer,
    ResidentEmergencyContactSerializer,
    ResidentPhotoSerializer,
    ResidentProfileSerializer,
    HelperIdentitySerializer,
    HelperAddressSerializer,
    HelperDocumentsSerializer,
    HelperServicesPricingSerializer,
    HelperExperienceSerializer,
    HelperAvailabilitySerializer,
    HelperEmergencyContactSerializer,
    HelperProfileSerializer,)

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
                        value={
                            "house_no": "12A",
                            "area": "Indirapuram",
                            "city": "Ghaziabad",
                            "pincode": "201014",
                            "latitude": "28.640000",
                            "longitude": "77.370000",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident \u2014 address (step 1)",
        description="Creates the resident profile if it doesn't exist yet and saves the address fields.",
    )
)
class ResidentAddressView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentAddressSerializer

@extend_schema_view(
    post=extend_schema(
        request=ResidentEmergencyContactSerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentEmergencyContactSerializer,
                description="Emergency contact saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"emergency_contact_name": "Tulika", "emergency_contact_mobile": "9876543210"},
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident \u2014 emergency contact (step 2)",
        description="Sets the emergency contact name and mobile number.",
    )
)
class ResidentEmergencyContactView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentEmergencyContactSerializer

@extend_schema_view(
    post=extend_schema(
        request=ResidentPhotoSerializer,
        responses={
            200: OpenApiResponse(
                response=ResidentPhotoSerializer,
                description="Profile photo saved",
                examples=[OpenApiExample("Success", value={"profile_photo": "/media/resident_photos/2026/07/photo.jpg"})],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident \u2014 profile photo (step 3)",
        description="Uploads the resident profile photo.",
    )
)
class ResidentPhotoView(ResidentProfileStepMixin, generics.GenericAPIView):
    serializer_class = ResidentPhotoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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
                            "latitude": "28.640000",
                            "longitude": "77.370000",
                            "emergency_contact_name": "Tulika",
                            "emergency_contact_mobile": "9876543210",
                            "profile_photo": "/media/resident_photos/2026/07/photo.jpg",
                        },
                    )
                ],
            ),
            401: _ERROR_401,
        },
        tags=["Resident Onboarding"],
        summary="Resident \u2014 full profile",
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
        profile, _ = HelperProfile.objects.get_or_create(user=self.request.user)
        return profile
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema_view(
    post=extend_schema(
        request=HelperIdentitySerializer,
        responses={
            200: OpenApiResponse(
                response=HelperIdentitySerializer,
                description="Identity details saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "full_name": "Sunita Devi",
                            "date_of_birth": "1990-05-12",
                            "govt_id_type": "aadhaar",
                            "govt_id_number": "1234 5678 9012",
                            "aadhaar_card": "/media/helper_docs/aadhaar/2026/07/aadhaar.jpg",
                            "pan_card": "/media/helper_docs/pan/2026/07/pan.jpg",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 identity verification (step 1)",
        description="Saves the helper's name, date of birth, government ID, Aadhaar card (required) and PAN card (optional).",
    )
)
class HelperIdentityView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperIdentitySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

@extend_schema_view(
    post=extend_schema(
        request=HelperAddressSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperAddressSerializer,
                description="Address saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "house_no": "7B",
                            "area": "Vaishali",
                            "city": "Ghaziabad",
                            "pincode": "201010",
                            "latitude": "28.650000",
                            "longitude": "77.340000",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 address (step 2)",
        description="Creates the helper profile if it doesn't exist yet and saves the address fields.",
    )
)
class HelperAddressView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperAddressSerializer

@extend_schema_view(
    post=extend_schema(
        request=HelperDocumentsSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperDocumentsSerializer,
                description="Photo and documents saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "profile_photo": "/media/helper_photos/2026/07/photo.jpg",
                            "police_verification_cert": "/media/helper_docs/police/2026/07/cert.pdf",
                            "address_proof": "/media/helper_docs/address_proof/2026/07/proof.pdf",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 profile photo & documents (step 3)",
        description="Uploads the helper profile photo, police verification certificate, and address proof.",
    )
)
class HelperDocumentsView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperDocumentsSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
@extend_schema_view(
    post=extend_schema(
        request=HelperServicesPricingSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperServicesPricingSerializer,
                description="Services & pricing saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "service_prices": [
                                {"service": 1, "price_per_hour": "200.00"},
                                {"service": 2, "price_per_hour": "150.00"},
                            ]
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 services & pricing (step 4)",
        description="Sets the services the helper offers along with the per-hour price for each service.",
    )
)
class HelperServicesPricingView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperServicesPricingSerializer
@extend_schema_view(
    post=extend_schema(
        request=HelperExperienceSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperExperienceSerializer,
                description="Experience & languages saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "years_of_experience": 3,
                            "languages_spoken": [1, 2],
                            "about": "Experienced in cooking and cleaning for family homes.",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 experience & languages (step 5)",
        description="Sets years of experience, Language IDs spoken, and an about description.",
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
                description="Availability saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "working_days": ["mon", "tue", "wed", "thu", "fri"],
                            "start_time": "09:00:00",
                            "end_time": "18:00:00",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 availability (step 6)",
        description="Sets the working days and the start and end working time.",
    )
)
class HelperAvailabilityView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperAvailabilitySerializer
@extend_schema_view(
    post=extend_schema(
        request=HelperEmergencyContactSerializer,
        responses={
            200: OpenApiResponse(
                response=HelperEmergencyContactSerializer,
                description="Emergency contact saved",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "emergency_contact_name": "Ramesh Kumar",
                            "emergency_contact_relation": "Spouse",
                            "emergency_contact_mobile": "9123456780",
                        },
                    )
                ],
            ),
            400: _ERROR_400,
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 emergency contact (step 7)",
        description="Sets the emergency contact name, relation, and phone number.",
    )
)
class HelperEmergencyContactView(HelperProfileStepMixin, generics.GenericAPIView):
    serializer_class = HelperEmergencyContactSerializer
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
                            "full_name": "Sunita Devi",
                            "date_of_birth": "1990-05-12",
                            "govt_id_type": "aadhaar",
                            "govt_id_number": "1234 5678 9012",
                            "aadhaar_card": "/media/helper_docs/aadhaar/2026/07/aadhaar.jpg",
                            "pan_card": "/media/helper_docs/pan/2026/07/pan.jpg",
                            "house_no": "7B",
                            "area": "Vaishali",
                            "city": "Ghaziabad",
                            "pincode": "201010",
                            "latitude": "28.650000",
                            "longitude": "77.340000",
                            "profile_photo": "/media/helper_photos/2026/07/photo.jpg",
                            "police_verification_cert": "/media/helper_docs/police/2026/07/cert.pdf",
                            "address_proof": "/media/helper_docs/address_proof/2026/07/proof.pdf",
                            "service_prices": [
                                {"service": {"id": 1, "name": "Cleaning", "slug": "cleaning"}, "price_per_hour": "200.00"},
                                {"service": {"id": 2, "name": "Cooking", "slug": "cooking"}, "price_per_hour": "150.00"},
                            ],
                            "years_of_experience": 3,
                            "languages_spoken": [
                                {"id": 1, "name": "Hindi", "code": "hi"},
                                {"id": 2, "name": "English", "code": "en"},
                            ],
                            "about": "Experienced in cooking and cleaning for family homes.",
                            "working_days": ["mon", "tue", "wed", "thu", "fri"],
                            "start_time": "09:00:00",
                            "end_time": "18:00:00",
                            "emergency_contact_name": "Ramesh Kumar",
                            "emergency_contact_relation": "Spouse",
                            "emergency_contact_mobile": "9123456780",
                        },
                    )
                ],
            ),
            401: _ERROR_401,
        },
        tags=["Helper Onboarding"],
        summary="Helper \u2014 full profile",
        description="Returns every onboarding step combined for the logged-in helper.",
    )
)
class HelperProfileDetailView(generics.RetrieveAPIView):
    serializer_class = HelperProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        profile, _ = HelperProfile.objects.get_or_create(user=self.request.user)
        return profile