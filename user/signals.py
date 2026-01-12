from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from vendor.models import VendorProfile



@receiver(post_save, sender=User)
def create_vendor_profile_on_user_creation(sender, instance:User, created, **kwargs):
    if created and instance.role == User.Role.VENDOR:
        VendorProfile.objects.create(instance)

