from django.urls import path
from webhook.views import IPNOrderConfirmAPIView

urlpatterns = [
    path("payment/<uuid:id>/", IPNOrderConfirmAPIView.as_view())
]
