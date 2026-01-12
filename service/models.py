from django.db import models
from vendor.models import VendorProfile
import uuid

class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True) #To identify if the service is still active or not

class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100) # e.g., "Premium", "Express", "Basic"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
