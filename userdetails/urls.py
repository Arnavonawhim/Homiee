from django.urls import path
from . import views

urlpatterns = [
    path("residents/address/", views.ResidentAddressView.as_view(), name="resident-address"),
    path("residents/emergency-contact/", views.ResidentEmergencyContactView.as_view(), name="resident-emergency-contact"),
    path("residents/photo/", views.ResidentPhotoView.as_view(), name="resident-photo"),
    path("residents/profile/", views.ResidentProfileDetailView.as_view(), name="resident-profile-detail"),
    path("helpers/identity/", views.HelperIdentityView.as_view(), name="helper-identity"),
    path("helpers/address/", views.HelperAddressView.as_view(), name="helper-address"),
    path("helpers/documents/", views.HelperDocumentsView.as_view(), name="helper-documents"),
    path("helpers/services/", views.HelperServicesPricingView.as_view(), name="helper-services"),
    path("helpers/experience/", views.HelperExperienceView.as_view(), name="helper-experience"),
    path("helpers/availability/", views.HelperAvailabilityView.as_view(), name="helper-availability"),
    path("helpers/emergency-contact/", views.HelperEmergencyContactView.as_view(), name="helper-emergency-contact"),
    path("helpers/profile/", views.HelperProfileDetailView.as_view(), name="helper-profile-detail"),
]
