import datetime
import auto_prefetch

from django.db import models

from base.models import BaseModel
from account.models import User


class Token(BaseModel):
    """Tracking user access token and refresh token"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    is_blacklisted = models.BooleanField(default=False)

    class Meta(auto_prefetch.Model.Meta):
        ordering = ["-updated"]
