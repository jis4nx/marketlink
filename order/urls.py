from django.urls import include, path

from order.views import RepairOrderViewSet
from rest_framework.routers import DefaultRouter




repair_order_router = DefaultRouter()
repair_order_router.register(r"", RepairOrderViewSet, basename="repairorder")

urlpatterns = [
    path("", include(repair_order_router.urls))
]
