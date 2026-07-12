from django.urls import path
from . import views

urlpatterns = [
    path("residents/address/", views.ResidentAddressView.as_view(), name="resident-address"),
    path("residents/emergency-contact/request-otp/", views.ResidentSOSRequestOTPView.as_view(), name="resident-sos-request-otp"),
    path("residents/emergency-contact/resend-otp/", views.ResidentSOSResendOTPView.as_view(), name="resident-sos-resend-otp"),
    path("residents/emergency-contact/verify-otp/", views.ResidentSOSVerifyOTPView.as_view(), name="resident-sos-verify-otp"),
    path("residents/photo/", views.ResidentPhotoView.as_view(), name="resident-photo"),
    path("residents/profile/", views.ResidentProfileDetailView.as_view(), name="resident-profile-detail"),
    path("helpers/identity/", views.HelperIdentityView.as_view(), name="helper-identity"),
    path("helpers/address/", views.HelperAddressView.as_view(), name="helper-address"),
    path("helpers/documents/", views.HelperDocumentsView.as_view(), name="helper-documents"),
    path("helpers/services/", views.HelperServicesPricingView.as_view(), name="helper-services"),
    path("helpers/experience/", views.HelperExperienceView.as_view(), name="helper-experience"),
    path("helpers/availability/", views.HelperAvailabilityView.as_view(), name="helper-availability"),
    path("helpers/emergency-contact/request-otp/", views.HelperSOSRequestOTPView.as_view(), name="helper-sos-request-otp"),
    path("helpers/emergency-contact/resend-otp/", views.HelperSOSResendOTPView.as_view(), name="helper-sos-resend-otp"),
    path("helpers/emergency-contact/verify-otp/", views.HelperSOSVerifyOTPView.as_view(), name="helper-sos-verify-otp"),
    path("helpers/profile/", views.HelperProfileDetailView.as_view(), name="helper-profile-detail"),
]
