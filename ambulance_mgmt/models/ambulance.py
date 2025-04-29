import auto_prefetch
from django.db import models
from base.models import BaseModel

class STATUS_CHOICES(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Avialable"
    BUSY = "BUSY", "Busy"
    OFFLINE = "OFFLINE", "Offline"
    
class TYPE_CHOICES(models.TextChoices):
    BLS = "BLS", "Basic Life Support"
    ALS = "ALS", "Advanced Life Support"
    MICU = "MICU", "Mobile Intensive Care Unit"
    

class Ambulance(BaseModel):
    ambulance_registration_number = models.CharField(max_length=50, unique=True, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES.values,
        default=STATUS_CHOICES.OFFLINE,
    )
    hospital = models.ForeignKey(
        'Hospital',
        on_delete=models.CASCADE,
        related_name='ambulances',
    )
    ambulance_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES.values,
        default=TYPE_CHOICES.BLS,
    )
    # assigned_to = models.OneToOneField('account.User')


    class Meta(auto_prefetch.Model.Meta):
        ordering = ['-updated']
        unique_together = ('ambulance_registration_number', 'hospital')

    def __str__(self):
        return f"{self.ambulance_id} ({self.get_ambulance_type_display()})"