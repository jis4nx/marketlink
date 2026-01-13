from rest_framework import serializers
from .models import RepairOrder
from order.services import create_repair_order, StockUnavailable



class RepairOrderListSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(
        source="variant.service.name", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )
    vendor_email = serializers.EmailField(
        source="vendor.email", read_only=True
    )

    class Meta:
        model = RepairOrder
        fields = (
            "order_id",
            "status",
            "total_amount",
            "service_name",
            "variant_name",
            "vendor_email",
            "created_at",
        )


class RepairOrderSerializer(serializers.ModelSerializer):
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = (
            "order_id",
            "customer",
            "vendor",
            "variant",
            "status",
            "total_amount",
            "payment_url",
            "created_at",
        )
        read_only_fields = (
            "order_id",
            "customer",
            "vendor",
            "status",
            "total_amount",
            "created_at",
        )

    def get_payment_url(self, obj):
        return f"https://payment.example.com/checkout/{obj.order_id}"

    def create(self, validated_data):
        user = self.context["request"].user
        variant = validated_data["variant"]

        try:
            return create_repair_order(user=user, variant=variant)
        except StockUnavailable:
            raise serializers.ValidationError(
                {"detail": "This service variant is fully booked."}
            )
