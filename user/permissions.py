from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsVendor(BasePermission):
    """
    Allows access only to users with a Vendor role
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_vendor


class IsServiceOwner(BasePermission):
    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_vendor:
            return False

        return obj.vendor == user.vendor_profile

class IsServiceVariantOwner(BasePermission):
    message = "You do not have permission to modify this service variant."

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_vendor:
            return False

        return obj.service.vendor == user.vendor_profile
