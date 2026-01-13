from django.db.models import TextChoices


class OrderStatus(TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"



class PaymentMethodChoice(TextChoices):
    SSLCOMMERZ = "sslcommerz", "SSLCommerz"
