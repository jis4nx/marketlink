import pytest

from user.choices import UserRole
from user.models import Admin, Customer
from vendor.models import Vendor


@pytest.mark.django_db
def test_create_user_requires_email(django_user_model):
    with pytest.raises(ValueError, match="Email field must be set"):
        django_user_model.objects.create_user(email=None, password="password")


@pytest.mark.django_db
def test_create_superuser_sets_required_flags(django_user_model):
    admin = django_user_model.objects.create_superuser(
        email="admin@example.com", password="AdminPass!123"
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.role == UserRole.ADMIN


@pytest.mark.django_db
def test_full_name_returns_first_and_last(create_user):
    user = create_user(first_name="Ada", last_name="Lovelace")
    assert user.full_name == "Ada Lovelace"


@pytest.mark.django_db
def test_role_specific_managers_filter_results(create_user, django_user_model):
    vendor = create_user(role=UserRole.VENDOR)
    customer = create_user(role=UserRole.CUSTOMER)
    admin = django_user_model.objects.create_superuser(
        email="owner@example.com", password="OwnerPass!123"
    )

    assert list(Vendor.objects.values_list("id", flat=True)) == [vendor.id]
    assert list(Customer.objects.values_list("id", flat=True)) == [customer.id]
    assert list(Admin.objects.values_list("id", flat=True)) == [admin.id]
