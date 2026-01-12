from django.urls import path
from service.views import ServiceListCreateView, ServiceRetrieveUpdateDestroyView, ServiceVariantCreateView


urlpatterns = [
    path("", ServiceListCreateView.as_view(), name="list-create-service"),
    path("<uuid:pk>/", ServiceRetrieveUpdateDestroyView.as_view(), name="get-delete-service"),
    path("variants/", ServiceVariantCreateView.as_view(), name="create-service-variant"),
]
