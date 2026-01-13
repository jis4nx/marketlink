from rest_framework.views import APIView
from rest_framework.response import Response
from order.models.repair_order import RepairOrder
from order.services import RepairOrderService
from rest_framework import status
from webhook.validators import hash_validate_ipn, validate_with_sslcommerz


class IPNOrderConfirmAPIView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data.dict()
        print("HELLLLLLO")

        if not hash_validate_ipn(post_body=data):
            print("validate_sslcommerz_hash")
            return Response(
                {"error": "Invalid verify_sign"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        val_id = data.get("val_id")
        if not val_id:
            return Response(
                {"error": "val_id missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validation = validate_with_sslcommerz(val_id)

        if validation.get("status") != "VALID":
            return Response(
                {"error": "Payment not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = RepairOrder.objects.get(order_id=kwargs["id"])
        except RepairOrder.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if str(order.total_amount) != validation.get("amount"):
            return Response(
                {"error": "Amount mismatch"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_service = RepairOrderService(order)
        order_service.confirm(val_id=val_id)

        return Response({"success": True}, status=status.HTTP_200_OK)
