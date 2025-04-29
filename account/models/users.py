import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


class ROLE_CHOICES(models.TextChoices):
    ADMIN = "ADMIN", "Admin"  # System admin role
    STAFF = "STAFF", "Staff"  # Hospital Staff role
    DISPATCHER = "DISPATCHER", "Dispatcher"  # Ambulance dispatcher role
    PATIENT = "PATIENT", "Patient"  # Patient user role


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password, **extra_fields):
        """
        Use email, password, and the additional fields to create and save user objects.
        """

        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Use email, password, and the additional fields to create and save superuser objects.
        """
        user = self.create_user(username, password, **extra_fields)
        user.is_superuser = True
        user.is_active = True
        user.is_verified = True
        user.is_staff = True

        user.save()
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=60, unique=True, db_index=True)
    first_name = models.CharField(_("first name"), max_length=1000)
    last_name = models.CharField(_("last name"), max_length=150)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(max_length=70, unique=True, db_index=True)
    is_mfa_enabled = models.BooleanField(default=False, null=True)
    address = models.TextField(null=True)

    # User role field
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES.choices, default=ROLE_CHOICES.PATIENT
    )

    # next of emergency contact
    emergency_first_name = models.CharField(_("first name"), max_length=1000)
    emergency_last_name = models.CharField(_("last name"), max_length=1000)
    emergency_phone_number = models.CharField(_("first name"), max_length=1000)
    emergency_address = models.TextField(null=True)

    # datetime
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()  # manager
    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-pk",)
