from django.contrib import admin
from bookings.models import Booking, Rating


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "resident", "helper", "service", "booking_date", "status", "total_amount")
    list_filter = ("status", "booking_date")
    search_fields = ("resident__username", "helper__username")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "helper", "resident", "score", "created_at")
    list_filter = ("score",)
    search_fields = ("helper__username", "resident__username")
