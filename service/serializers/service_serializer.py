from rest_framework import serializers
from service.models import Service, ServiceVariant


class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = (
            "id",
            "service",
            "name",
            "price",
            "estimated_minutes",
            "stock",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceVariantNestedSerializer(ServiceVariantSerializer):
    """ Service Serializer uses this serializer for Multiple Variant Creation on Service Creation"""
    class Meta(ServiceVariantSerializer.Meta):
        read_only_fields = ("id", "created_at", "updated_at", "service")


class ServiceSerializer(serializers.ModelSerializer):
    variants = ServiceVariantNestedSerializer(many=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Service
        fields = ("id", "vendor", "name", "description", "variants", "created_at")
        read_only_fields = ("id", "vendor", "created_at")

    def create(self, validated_data):
        variants_data = validated_data.pop("variants")

        service = Service.objects.create(**validated_data)

        for variant_data in variants_data:
            ServiceVariant.objects.create(service=service, **variant_data)
        return service


class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "vendor", "name", "description", "created_at")
