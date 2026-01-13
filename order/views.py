from os import wait
from rest_framework.response import Response
from order.choices import OrderStatus
from order.models.repair_order import RepairOrder
from order.serializers import RepairOrderSerializer, RepairOrderListSerializer
from rest_framework import mixins, status, viewsets, permissions
from django.shortcuts import get_object_or_404
from order.services import RepairOrderService
from user.permissions import IsCustomer, IsVendor
from rest_framework.views import APIView


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


class RepairOrderCompleteView(APIView):
    permission_classes = [IsVendor]

    def post(self, request, pk):
        order = get_object_or_404(RepairOrder, order_id=pk)

        if order.vendor != request.user.vendor_profile:
            return Response({"error": "Unauthorized access to this order."}, status=403)

        service = RepairOrderService(order)
        success, message = service.mark_as_completed()

        if not success:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": "order marked as completed"}, status=status.HTTP_200_OK
        )
