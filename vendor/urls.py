from django.urls import path

from vendor.views import VendorProfileView
urlpatterns = [
    path("profile/", VendorProfileView.as_view(), name="vendor-profile")
]
