from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import uuid
from user.managers import AdminManager, CustomerManager, UserManager
from user.choices import UserRole


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with roles"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return self.role == UserRole.CUSTOMER

    @property
    def is_vendor(self):
        return self.role == UserRole.VENDOR

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Customer(User):
    objects = CustomerManager()

    class Meta:
        proxy = True


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True
