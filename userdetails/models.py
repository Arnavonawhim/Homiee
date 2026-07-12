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

class ResidentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resident_profile")
    house_no = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_mobile = models.CharField(max_length=15)
    emergency_contact_verified = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to="resident_photos/%Y/%m/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class HelperProfile(models.Model):
    class GovtIdType(models.TextChoices):
        AADHAAR = "aadhaar", "Aadhaar Card"
        PAN = "pan", "PAN Card"
        VOTER_ID = "voter_id", "Voter ID"
        DRIVING_LICENSE = "driving_license", "Driving License"

    class Day(models.TextChoices):
        MON = "mon", "Monday"
        TUE = "tue", "Tuesday"
        WED = "wed", "Wednesday"
        THU = "thu", "Thursday"
        FRI = "fri", "Friday"
        SAT = "sat", "Saturday"
        SUN = "sun", "Sunday"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="helper_profile")
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    govt_id_type = models.CharField(max_length=20, choices=GovtIdType.choices, blank=True)
    govt_id_number = models.CharField(max_length=50, blank=True)
    aadhaar_card = models.FileField(upload_to="helper_docs/aadhaar/%Y/%m/", null=True, blank=True)
    adhaar_verified = models.BooleanField(default=False)
    pan_verified = models.BooleanField(default=False)
    pan_card = models.FileField(upload_to="helper_docs/pan/%Y/%m/", null=True, blank=True)
    house_no = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    profile_photo = models.ImageField(upload_to="helper_photos/%Y/%m/", null=True, blank=True)
    police_verification_cert = models.FileField(upload_to="helper_docs/police/%Y/%m/", null=True, blank=True)
    address_proof = models.FileField(upload_to="helper_docs/address_proof/%Y/%m/", null=True, blank=True)
    services_offered = models.ManyToManyField("Service", through="HelperServicePrice", related_name="helper_profiles")
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    languages_spoken = models.ManyToManyField("Language", related_name="helper_profiles")
    about = models.TextField(blank=True)
    working_days = models.JSONField(default=list)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    emergency_contact_mobile = models.CharField(max_length=15, blank=True)
    emergency_contact_verified = models.BooleanField(default=False)
    avg_rating = models.FloatField(default=0,max_length=2,blank=True) 
    rating_count = models.IntegerField(default=0,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class HelperServicePrice(models.Model):
    helper = models.ForeignKey("HelperProfile", on_delete=models.CASCADE, related_name="service_prices")
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="helper_prices")
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ("helper", "service")
