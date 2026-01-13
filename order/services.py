from django.db import transaction
from django.core.cache import cache
from django.db.models import F
from order.choices import OrderStatus
from service.models import ServiceVariant
from order.models import RepairOrder

RESERVATION_TTL = 300


class StockUnavailable(Exception):
    pass


def create_repair_order(*, user, variant):
    redis_stock_key = f"variant:{variant.id}:stock"
    redis_reservation_key = f"order:{variant.id}:{user.id}:reservation"

    # Initialize Redis if missing
    cache.add(redis_stock_key, variant.stock, timeout=None)

    remaining = cache.decr(redis_stock_key)
    if remaining < 0:
        cache.incr(redis_stock_key)
        raise StockUnavailable()

    cache.set(redis_reservation_key, True, timeout=RESERVATION_TTL)

    try:
        with transaction.atomic():
            updated = (
                ServiceVariant.objects
                .filter(id=variant.id, stock__gt=0)
                .update(stock=F("stock") - 1)
            )

            if updated == 0:
                raise StockUnavailable()

            order = RepairOrder.objects.create(
                customer=user,
                vendor=variant.service.vendor,
                variant=variant,
                total_amount=variant.price,
                status=OrderStatus.PENDING,
            )

            return order

    except Exception:
        cache.incr(redis_stock_key)
        cache.delete(redis_reservation_key)
        raise
