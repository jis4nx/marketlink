from django.db import models
from django.conf import settings
import uuid
from user.models import User
from user.managers import VendorManager


class VendorProfile(models.Model):
    """Vendor profile linked to User"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )
    business_name = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendor_profiles"
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"

    def __str__(self):
        return self.business_name


class Vendor(User):
    objects = VendorManager()
    class Meta:
        proxy = True

    @property
    def profile(self):
        return self.vendor_profile
