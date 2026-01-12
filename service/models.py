from django.db import models
from vendor.models import VendorProfile
import uuid
from django.core.exceptions import ValidationError


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        VendorProfile, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(
        default=True
    )  # To identify if the service is still active or not
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.vendor.email}"

    def clean(self):
        if not self.vendor.is_active:
            raise ValidationError("Only active vendors can create services.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ServiceVariant(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=100)  # e.g., "Premium", "Express", "Basic"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_variants"
        verbose_name = "Service Variant"
        verbose_name_plural = "Service Variants"
        unique_together = ["service", "name"]

    def __str__(self):
        return f"{self.service.name} - {self.name}"
