from django.urls import path
from service.views.services import ServiceListCreateView, ServiceRetrieveUpdateDestroyView
from service.views.variants import ServiceVariantViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include

service_variant_router = DefaultRouter()
service_variant_router.register(r"variants", ServiceVariantViewSet, basename="service-variant")

urlpatterns = [
    path("", ServiceListCreateView.as_view(), name="list-create-service"),
    path("<uuid:pk>/", ServiceRetrieveUpdateDestroyView.as_view(), name="get-delete-service"),
    path("", include(service_variant_router.urls))
]

