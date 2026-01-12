from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from vendor.serializers.vendor_profile import VendorProfileSerializer
from rest_framework import permissions
from vendor.models import VendorProfile



class VendorProfileView(RetrieveUpdateAPIView):
    """Get and update vendor profile"""
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        vendor_profile, created = VendorProfile.objects.get_or_create(
            user=self.request.user
        )
        return vendor_profile
