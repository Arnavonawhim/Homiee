from django.conf import settings
from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)  

    def __str__(self):
        return self.name
    

class IdentityDocument(models.Model):
    class DocType(models.TextChoices):
        AADHAAR = "aadhaar", "Aadhaar Card"
        PAN = "pan", "PAN Card"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    file = models.FileField(upload_to="identity_docs/%Y/%m/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "doc_type")


class ResidentProfile(models.Model):
    class TimeSlot(models.TextChoices):
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"

    class Day(models.TextChoices):
        MON = "mon", "Monday"
        TUE = "tue", "Tuesday"
        WED = "wed", "Wednesday"
        THU = "thu", "Thursday"
        FRI = "fri", "Friday"
        SAT = "sat", "Saturday"
        SUN = "sun", "Sunday"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resident_profile")
    house_no = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Type of Help Needed
    services_needed = models.ManyToManyField("Service", related_name="resident_profiles")

    # Schedule
    work_type = models.CharField(max_length=100, blank=True)
    preferred_time_slots = models.JSONField(default=list) 
    days_required = models.JSONField(default=list)       

    # Safety & Identity
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_mobile = models.CharField(max_length=15)

    updated_at = models.DateTimeField(auto_now=True)



class HelperProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="helper_profile")
    services_offered = models.ManyToManyField("Service", related_name="helper_profiles")
    years_of_experience = models.PositiveSmallIntegerField()
    previous_work_reference = models.CharField(max_length=255, blank=True)
    languages_spoken = models.ManyToManyField("Language", related_name="helper_profiles")
    work_preference = models.CharField(max_length=50, blank=True)   
    working_hours = models.CharField(max_length=50, blank=True)
    areas_willing_to_work_in = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_mobile = models.CharField(max_length=15)

    updated_at = models.DateTimeField(auto_now=True)