from django.urls import include, path

from order.views import RepairOrderViewSet, RepairOrderCompleteView
from rest_framework.routers import DefaultRouter


repair_order_router = DefaultRouter()
repair_order_router.register(r"", RepairOrderViewSet, basename="repairorder")

urlpatterns = [
    path("", include(repair_order_router.urls)),
    path("mark-completed/<uuid:pk>/", RepairOrderCompleteView.as_view(), name="mark-completed"),
]
