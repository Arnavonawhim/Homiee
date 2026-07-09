from django.urls import path
from bookings import views

app_name = "bookings"

urlpatterns = [
    path("helpers/nearby/", views.NearbyHelpersView.as_view(), name="helpers-nearby"),
    path("helpers/category/", views.HelpersByCategoryView.as_view(), name="helpers-category"),
    path("helpers/search/", views.SearchHelpersView.as_view(), name="helpers-search"),
    path("helpers/<int:helper_id>/", views.HelperDetailView.as_view(), name="helper-detail"),
    path("bookings/", views.CreateBookingView.as_view(), name="booking-create"),
    path("bookings/mine/", views.MyBookingsView.as_view(), name="booking-mine"),
    path("bookings/incoming/", views.IncomingBookingsView.as_view(), name="booking-incoming"),
    path("bookings/<int:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<int:pk>/respond/", views.BookingRespondView.as_view(), name="booking-respond"),
    path("bookings/<int:pk>/complete/", views.CompleteBookingView.as_view(), name="booking-complete"),
    path("bookings/<int:pk>/cancel/", views.CancelBookingView.as_view(), name="booking-cancel"),
    path("bookings/<int:pk>/rate/", views.RateHelperView.as_view(), name="booking-rate"),
]
