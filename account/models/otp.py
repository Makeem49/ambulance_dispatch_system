import datetime
import auto_prefetch

from django.db import models

from base.models import BaseModel
from account.models import User


class OTP(BaseModel):
    """
    Model for storing One-Time Password (OTP) codes for user authentication.

    This model manages the storage and validation of OTP codes used for various
    authentication purposes such as email verification, password reset, and
    two-factor authentication.

    Attributes:
        user (User): Foreign key to the user model
        code (str): The 6-digit OTP code
        expires_at (datetime): Timestamp when the OTP code expires
        purpose (str): The purpose for which the OTP was generated
        created_at (datetime): Timestamp of when the OTP was created
        updated_at (datetime): Timestamp of the last update to the OTP
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    purpose = models.CharField(max_length=255)

    class Meta(auto_prefetch.Model.Meta):
        ordering = ["-updated"]

    def is_valid(self):
        return self.expires_at > datetime.datetime.now(datetime.timezone.utc)
