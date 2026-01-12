from rest_framework import serializers
from user.serializers.user_serializer import UserSerializer
from vendor.models import VendorProfile

class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ('id', 'user', 'business_name', 'address', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_active')
