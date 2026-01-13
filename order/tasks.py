from celery import shared_task
from order.choices import OrderStatus
from order.models.repair_order import RepairOrder

@shared_task
def send_invoice_task(order_id):
    order = RepairOrder.objects.get(order_id=order_id)

    # Logic to generate PDF and send email
    print(f"Sending invoice for {order_id} to {order.customer.email}")

@shared_task
def start_repair_processing_task(order_id):
    order = RepairOrder.objects.get(order_id=order_id)
    print(f"Starting repair workflow for {order_id}")
    order.status = OrderStatus.PROCESSING
    order.save(update_fields=["status"])
