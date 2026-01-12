from rest_framework import serializers
from service.models import Service, ServiceVariant


class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = ('id', 'name', 'price', 'estimated_minutes', 'stock', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ServiceSerializer(serializers.ModelSerializer):
    variants = ServiceVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ('id', 'vendor', 'name', 'description', 'variants', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing services"""
    class Meta:
        model = Service
        fields = ('id', 'vendor', 'name', 'description', 'created_at')
