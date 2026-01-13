from decimal import Decimal
from os import wait
from django.db import transaction
from django.core.cache import cache
from django.db.models import F
from order.choices import OrderStatus, PaymentMethodChoice
from service.models import ServiceVariant
from order.models.repair_order import RepairOrder
from order.models.payment import SSLCommerzData
from webhook.services.payment import SSLCommerzPayment
from order.tasks import (
    start_repair_processing_task,
    send_invoice_task,
    send_repair_ready_notification,
)

RESERVATION_TTL = 300


class StockUnavailable(Exception):
    pass


class RepairOrderService:
    def __init__(self, order: RepairOrder):
        self.order = order

    @classmethod
    def init(cls, user, variant, payment_method):
        redis_stock_key = f"variant:{variant.id}:stock"

        # Atomic Decrement
        cache.add(redis_stock_key, variant.stock, timeout=None)
        remaining = cache.decr(redis_stock_key)

        if remaining < 0:
            cache.incr(redis_stock_key)
            raise Exception("Stock Unavailable (Redis)")

        try:
            # Using F() expression prevents race conditions at the DB level
            with transaction.atomic():
                updated = ServiceVariant.objects.filter(
                    id=variant.id, stock__gt=0
                ).update(stock=F("stock") - 1)

                if updated == 0:
                    raise Exception("Stock Unavailable (Database)")

                order = RepairOrder.objects.create(
                    customer=user,
                    vendor=variant.service.vendor,
                    variant=variant,
                    total_amount=variant.price,
                    status=OrderStatus.PENDING,
                    payment_method=payment_method,
                )

            service_instance = cls(order)
            payment_gateway = service_instance.get_payment_service()
            payment_response = payment_gateway.init(order)

            if payment_response.get("status") == "SUCCESS":
                order.payment_url = payment_response.get("GatewayPageURL")
                return order
            else:
                service_instance.reject()
                raise Exception(
                    f"Payment Gateway Error: {payment_response.get('failedreason')}"
                )

        except Exception as e:
            # ROLLBACK: Safety net for unexpected errors
            # If order wasn't created, manually increment Redis back.
            # If order was created, the .reject() method above handles it.
            if "order" not in locals():
                cache.incr(redis_stock_key)
            raise e

    def confirm(self, val_id: str):
        """Processes the Webhook/IPN confirmation with amount verification"""
        payment_service = self.get_payment_service()
        data = payment_service.validate(val_id=val_id)

        if data.get("status") in ["VALID", "VALIDATED"]:

            # Amount Verification
            paid_amount = Decimal(str(data.get("amount", 0)))
            expected_amount = self.order.total_amount

            if paid_amount != expected_amount:
                print(
                    f"CRITICAL: Amount mismatch! Paid: {paid_amount}, Expected: {expected_amount}"
                )
                self.reject()
                return

            # 3. Atomic Update and Task Enqueue
            with transaction.atomic():
                self.order.status = OrderStatus.PAID
                self.order.save(update_fields=["status"])

                self.create_payment_data(data=data)

                transaction.on_commit(
                    lambda: send_invoice_task.delay(self.order.order_id)
                )
                transaction.on_commit(
                    lambda: start_repair_processing_task.delay(self.order.order_id)
                )

        else:
            self.reject()

    def reject(self):
        """Handles failed payments and restores stock"""
        self._restore_stock()
        self.order.status = OrderStatus.FAILED
        self.order.save(update_fields=["status"])

    def cancel(self):
        """Handles user cancellation and restores stock"""
        self._restore_stock()
        self.order.status = OrderStatus.CANCELLED
        self.order.save(update_fields=["status"])

    def mark_as_completed(self):
        """
        Transitions the order from PAID to COMPLETED.
        This represents the physical repair being finished.
        """
        if self.order.status != OrderStatus.PROCESSING:
            return False, f"Cannot complete an order with status: {self.order.status}"

        try:
            with transaction.atomic():
                self.order.status = OrderStatus.COMPLETED
                self.order.save(update_fields=["status"])

                transaction.on_commit(
                    lambda: send_repair_ready_notification.delay(self.order.order_id)
                )

            return True, "Order marked as completed"

        except Exception as e:
            return False, str(e)

    def _restore_stock(self):
        """Helper to increment stock back in DB and Redis"""
        variant = self.order.variant
        variant.stock = F("stock") + 1
        variant.save(update_fields=["stock"])
        cache.incr(f"variant:{variant.id}:stock")

    def get_payment_service(self):
        if self.order.payment_method == PaymentMethodChoice.SSLCOMMERZ:
            return SSLCommerzPayment()
        # Add other gateways here (Stripe, AmarPay, etc.)
        raise NotImplementedError("Payment method not supported")

    def create_payment_data(self, data: dict):
        return SSLCommerzData.objects.create(
            order=self.order,
            val_id=data.get("val_id"),
            tran_id=data.get("tran_id"),
            amount=data.get("amount"),
            card_type=data.get("card_type"),
        )
