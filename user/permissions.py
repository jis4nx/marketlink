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
