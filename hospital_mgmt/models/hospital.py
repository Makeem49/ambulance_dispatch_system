import auto_prefetch
from django.db import models
from base.models import BaseModel

class Hospital(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)


    class Meta(auto_prefetch.Model.Meta):
        ordering = ['-updated']
        unique_together = ('title', 'address')

    def __str__(self):
        return self.name