from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from authentication.models import User

@admin.register(User)
class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "fname", "lname", "email", "mobile", "username", "is_email_verified", "is_mobile_verified", "is_active", "is_admin", "created_at"]
    list_filter = ["is_admin", "is_active", "is_email_verified", "is_mobile_verified", "created_at"]
    search_fields = ["email", "username", "fname", "lname", "mobile"]
    ordering = ["-created_at"]
    filter_horizontal = []
    fieldsets = [
        ("Identity", {"fields": ["fname", "lname", "email", "mobile", "username", "password"]}),
        ("Google", {"fields": ["google_id"]}),
        ("Permissions", {"fields": ["is_admin", "is_active", "is_email_verified", "is_mobile_verified"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at", "last_login"]}),
    ]
    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["fname", "lname", "email", "mobile", "username", "password1", "password2"],
        })
    ]

    readonly_fields = ["created_at", "updated_at", "last_login"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["email", "username"]
        return self.readonly_fields

admin.site.site_header = "MaidEasy Admin"
admin.site.site_title = "MaidEasy Admin Portal"
admin.site.index_title = "Welcome to MaidEasy Admin"