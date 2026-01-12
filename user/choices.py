from django.db.models import TextChoices
class UserRole(TextChoices):
    CUSTOMER = 'customer', 'Customer'
    VENDOR = 'vendor', 'Vendor'
    ADMIN = 'admin', 'Admin'


