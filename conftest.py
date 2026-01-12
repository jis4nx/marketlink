import pytest
from itertools import count

from user.choices import UserRole


@pytest.fixture(scope="session")
def email_counter():
    return count(start=1)


@pytest.fixture
def create_user(django_user_model, email_counter):
    def _create_user(**overrides):
        idx = next(email_counter)
        defaults = {
            "email": f"user{idx}@example.com",
            "password": "StrongPass!123",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.CUSTOMER,
            "is_active": True,
        }
        defaults.update(overrides)
        return django_user_model.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def vendor_user(create_user):
    return create_user(role=UserRole.VENDOR)


@pytest.fixture
def vendor_profile(vendor_user):
    from vendor.models import VendorProfile

    return VendorProfile.objects.create(
        user=vendor_user,
        business_name="Acme Supplies",
        address="123 Market Street",
        is_active=True,
    )
