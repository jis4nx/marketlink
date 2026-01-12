from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from service.serializers.service_serializer import (
    ServiceSerializer,
    ServiceListSerializer,
    ServiceVariantSerializer,
)
from service.models import Service
from user.permissions import IsVendor


class ServiceListCreateView(generics.ListCreateAPIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsVendor()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ServiceSerializer
        return ServiceListSerializer

    def get_queryset(self):
        if self.request.user.is_vendor:
            return Service.objects.filter(vendor=self.request.user.vendor_profile, is_active=True)
        return Service.objects.filter(vendor__is_active=True, is_active=True)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)


class ServiceRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    ...


class ServiceVariantCreateView(generics.CreateAPIView):
    serializer_class = ServiceVariantSerializer

    def perform_create(self, serializer):
        service = serializer.validated_data["service"]

        if service.vendor != self.request.user.vendor:
            raise PermissionDenied("You do not own this service")

        serializer.save()
