from django.db import models
from django.conf import settings
from order.choices import OrderStatus
from service.models import ServiceVariant
from vendor.models import VendorProfile
from django.core.exceptions import ValidationError
import uuid


class RepairOrder(models.Model):
    """Repair order created by customer"""

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_as_customer",
    )
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name="orders_as_vendor",
    )
    variant = models.ForeignKey(
        ServiceVariant, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repair_orders"
        verbose_name = "Repair Order"
        verbose_name_plural = "Repair Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def clean(self):
        super().clean()
        if self.customer and not self.customer.is_customer:
            raise ValidationError(
                {"customer": "Selected user must have CUSTOMER role."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.email}"
