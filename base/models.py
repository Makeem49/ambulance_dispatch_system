import auto_prefetch
from django.db import models


class BaseModel(auto_prefetch.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = auto_prefetch.Manager()

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
