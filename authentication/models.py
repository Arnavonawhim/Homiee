from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")
        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)
        else:
            extra_fields["email"] = None
        if not extra_fields.get("mobile"):
            extra_fields["mobile"] = None
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_email_verified", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    fname = models.CharField(verbose_name="First Name", max_length=30)
    lname = models.CharField(verbose_name="Last Name", max_length=30)
    role = models.TextChoices()
    email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True, blank=True, null=True, db_index=True)
    mobile = models.CharField(verbose_name="Mobile Number", max_length=15, unique=True, blank=True, null=True, db_index=True)
    username = models.CharField(verbose_name="Username", max_length=15, unique=True, db_index=True)
    google_id = models.CharField(verbose_name="Google ID", max_length=255, unique=True, blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["fname", "lname"]

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.username})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]