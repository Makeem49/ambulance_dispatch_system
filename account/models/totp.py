import datetime
import auto_prefetch

from django.db import models

from base.models import BaseModel
from account.models import User
    
class TOTPAuth(BaseModel):
    """
    Model for storing Time-based One-Time Password (TOTP) authentication settings for users.
    
    This model manages the TOTP two-factor authentication configuration for users,
    including the secret key, verification status, and related metadata.
    
    Attributes:
        user (User): One-to-one relationship with the user model
        otp_enabled (bool): Whether TOTP is enabled for the user
        otp_verified (bool): Whether the TOTP setup has been verified
        otp_base32 (str): Base32 encoded secret key for TOTP generation
        otp_auth_url (str): URL for QR code generation during TOTP setup
        created_at (datetime): Timestamp of when the TOTP record was created
        updated_at (datetime): Timestamp of the last update to the TOTP record
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="totp_auth"
    )
    otp_enabled = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    otp_base32 = models.CharField(max_length=255, null=True, blank=True)
    otp_auth_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns a string representation of the TOTP auth record."""
        return str(self.user)

    class Meta(auto_prefetch.Model.Meta):
        """Metadata options for the TOTPAuth model."""
        ordering = ['-created_at']