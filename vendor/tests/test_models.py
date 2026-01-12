import pytest


@pytest.mark.django_db
def test_vendor_profile_string_representation(vendor_profile):
    assert str(vendor_profile) == "Acme Supplies"


@pytest.mark.django_db
def test_vendor_proxy_profile_property_returns_profile(vendor_profile):
    from vendor.models import Vendor
    
    vendor = Vendor.objects.get(id=vendor_profile.user.id)
    
    assert vendor.profile == vendor_profile
