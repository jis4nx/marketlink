from django.urls import path
from service.views import ServiceListCreateView, ServiceVariantCreateView


urlpatterns = [
    path("", ServiceListCreateView.as_view(), name="list-create-service"),
    path("variants/", ServiceVariantCreateView.as_view(), name="create-service-variant"),
]
