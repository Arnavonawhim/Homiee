from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Language, HelperProfile, HelperServicePrice

admin.site.register(Service)
admin.site.register(Language)


def _file_preview(file_field, label):
    if not file_field:
        return "Not uploaded"
    url = file_field.url
    if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        return format_html(
            '<a href="{}" target="_blank"><img src="{}" style="max-height:220px;border-radius:6px;"></a>',
            url, url,
        )
    return format_html('<a href="{}" target="_blank">{}</a>', url, label)


class HelperServicePriceInline(admin.TabularInline):
    model = HelperServicePrice
    extra = 0


@admin.register(HelperProfile)
class HelperProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "id_verified", "police_verified", "docs_uploaded", "updated_at")
    list_filter = ("id_verified", "police_verified", "city", "govt_id_type")
    search_fields = ("full_name", "user__email", "user__mobile", "govt_id_number")
    list_select_related = ("user",)
    inlines = [HelperServicePriceInline]
    readonly_fields = (
        "photo_preview", "front_card_preview", "back_card_preview",
        "police_cert_preview", "updated_at",
    )
    actions = ["approve_identity", "approve_police", "approve_all", "revoke_all"]

    fieldsets = (
        ("Helper", {"fields": ("user", "full_name", "date_of_birth", "photo_preview", "profile_photo")}),
        ("Identity verification", {
            "fields": (
                "govt_id_type", "govt_id_number",
                "front_card_preview", "front_card",
                "back_card_preview", "back_card",
                "id_verified",
            ),
        }),
        ("Police verification", {
            "fields": ("police_cert_preview", "police_verification_cert", "police_verified"),
        }),
        ("Address", {"fields": ("house_no", "state", "area", "city", "pincode", "latitude", "longitude")}),
        ("Work", {
            "fields": (
                "years_of_experience", "languages_spoken", "about",
                "working_days", "start_time", "end_time",
            ),
        }),
        ("Emergency contact", {
            "fields": (
                "emergency_contact_name", "emergency_contact_relation",
                "emergency_contact_mobile", "emergency_contact_verified",
            ),
        }),
        ("Ratings", {"fields": ("avg_rating", "rating_count", "updated_at")}),
    )

    @admin.display(boolean=True, description="Docs uploaded")
    def docs_uploaded(self, obj):
        return bool(obj.front_card and obj.police_verification_cert)

    @admin.display(description="Profile photo")
    def photo_preview(self, obj):
        return _file_preview(obj.profile_photo, "View photo")

    @admin.display(description="ID front")
    def front_card_preview(self, obj):
        return _file_preview(obj.front_card, "View front")

    @admin.display(description="ID back")
    def back_card_preview(self, obj):
        return _file_preview(obj.back_card, "View back")

    @admin.display(description="Police certificate")
    def police_cert_preview(self, obj):
        return _file_preview(obj.police_verification_cert, "View certificate")

    @admin.action(description="Approve identity (ID) for selected helpers")
    def approve_identity(self, request, queryset):
        count = queryset.update(id_verified=True)
        self.message_user(request, f"{count} helper(s) ID-verified.")

    @admin.action(description="Approve police verification for selected helpers")
    def approve_police(self, request, queryset):
        count = queryset.update(police_verified=True)
        self.message_user(request, f"{count} helper(s) police-verified.")

    @admin.action(description="Approve ID and police verification")
    def approve_all(self, request, queryset):
        count = queryset.update(id_verified=True, police_verified=True)
        self.message_user(request, f"{count} helper(s) fully verified.")

    @admin.action(description="Revoke all verification")
    def revoke_all(self, request, queryset):
        count = queryset.update(id_verified=False, police_verified=False)
        self.message_user(request, f"{count} helper(s) un-verified.")