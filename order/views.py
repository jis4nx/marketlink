from order.models import RepairOrder
from order.serializers import RepairOrderSerializer, RepairOrderListSerializer
from rest_framework import mixins, viewsets, permissions

from user.permissions import IsCustomer


class RepairOrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List orders or create a new order"""

    def get_serializer_class(self):
        if self.action == "list":
            return RepairOrderListSerializer
        return RepairOrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsCustomer()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        qs = RepairOrder.objects.select_related(
            "vendor",
            "variant",
            "variant__service",
            "customer",
        )

        if user.is_customer:
            return qs.filter(customer=user)

        if user.is_vendor:
            return qs.filter(vendor=user.vendor_profile)
        return qs
