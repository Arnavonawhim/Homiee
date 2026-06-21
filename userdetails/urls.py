# profiles/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("residents/address/", views.ResidentAddressView.as_view(), name="resident-address"),
    path("residents/services-needed/", views.ResidentServicesNeededView.as_view(), name="resident-services-needed"),
    path("residents/schedule/", views.ResidentScheduleView.as_view(), name="resident-schedule"),
    path("residents/safety/", views.ResidentSafetyView.as_view(), name="resident-safety"),
    path("residents/profile/", views.ResidentProfileDetailView.as_view(), name="resident-profile-detail"),
    path("helpers/services-offered/", views.HelperServicesOfferedView.as_view(), name="helper-services-offered"),
    path("helpers/experience/", views.HelperExperienceView.as_view(), name="helper-experience"),
    path("helpers/availability/", views.HelperAvailabilityView.as_view(), name="helper-availability"),
    path("helpers/profile/", views.HelperProfileDetailView.as_view(), name="helper-profile-detail"),
]