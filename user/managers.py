from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager
from user.choices import UserRole



class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class VendorManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=UserRole.VENDOR)

class CustomerManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=UserRole.CUSTOMER)

class AdminManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=UserRole.ADMIN)
