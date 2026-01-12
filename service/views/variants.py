from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from service.models import ServiceVariant
from service.serializers.service_serializer import ServiceVariantSerializer
from user.permissions import IsServiceVariantOwner
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class ServiceVariantViewSet(ModelViewSet):
    queryset = ServiceVariant.objects.select_related("service", "service__vendor")
    serializer_class = ServiceVariantSerializer

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [
                permissions.IsAuthenticated(),
                IsServiceVariantOwner(),
            ]
        return [
            permissions.IsAuthenticated(),
        ]

    def perform_create(self, serializer):
        service = serializer.validated_data["service"]
        user = self.request.user

        if not user.is_vendor or service.vendor != user.vendor_profile:
            raise PermissionDenied("You do not own this service")

        serializer.save()
