from django.conf import settings
import requests
from typing import Dict, Any
from decouple import config


class SSLCommerzPayment:
    def __init__(self):
        self.session_url = config("SSLCOMMERZ_SESSION_URL")
        self.validation_url = config("SSLCOMMERZ_VALIDATION_URL")
        self.store_id = config("SSLCOMMERZ_STORE_ID")
        self.store_passwd = config("SSLCOMMERZ_STORE_PASS")

        self.base_domain = config("BASE_DOMAIN", default="http://localhost:8000")

        self.default_params = {
            "store_id": self.store_id,
            "store_passwd": self.store_passwd,
        }

    def init(self, order) -> Dict[str, Any]:
        """
        Initialize a payment session for a RepairOrder.
        """
        ipn_url = f"https://frida-unsystematising-criminally.ngrok-free.dev/webhooks/payment/{order.order_id}/"
        payload = {
            **self.default_params,
            "total_amount": float(order.total_amount),
            "currency": "BDT",
            "tran_id": f"{order.order_id}",
            "success_url": f"{self.base_domain}/orders/success/",
            "fail_url": f"{self.base_domain}/orders/fail/",
            "cancel_url": f"{self.base_domain}/orders/cancel/",
            # Customer Info from the User model
            "cus_name": order.customer.full_name,
            "cus_email": order.customer.email,
            "cus_phone": getattr(order.customer, "phone_number", "01700000000"),
            "cus_add1": "",
            "cus_city": "",
            "cus_country": "",
            "shipping_method": "NO",
            "num_of_item": 1,
            "product_name": f"{order.variant.service.name} - {order.variant.name}",
            "product_category": "Vehicle Repair",
            "product_profile": "general",
        }
        payload["ipn_url"] = ipn_url.strip()
        try:
            response = requests.post(self.session_url, data=payload, timeout=10)
            if response.status_code == 200:
                return response.json()

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"SSLCommerz Connection Error: {e}")
            raise Exception("Payment gateway communication failed.")

    def validate(self, val_id: str) -> Dict[str, Any]:
        """
        Validate a payment via SSLCommerz Validator API.
        """
        params = {
            **self.default_params,
            "val_id": val_id,
            "format": "json",
            "v": "1",
        }

        try:
            response = requests.get(self.validation_url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()

            raise Exception(f"Validation failed with status {response.status_code}")
        except requests.exceptions.RequestException:
            raise Exception("Payment verification service unavailable.")
