from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from django.conf import settings
from yookassa import Configuration, Payment

from store.models import Order


def _ensure_configuration() -> None:
    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        raise RuntimeError('YooKassa credentials are not configured')
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(order: Order, return_url: str, description: str) -> Payment:
    _ensure_configuration()
    payment = Payment.create(
        {
            'amount': {'value': f'{order.total_amount:.2f}', 'currency': order.currency},
            'confirmation': {'type': 'redirect', 'return_url': return_url},
            'capture': True,
            'description': description,
            'metadata': {'order_id': order.id},
        },
        uuid.uuid4(),
    )
    order.payment_id = payment.id
    order.status = Order.STATUS_AWAITING
    order.save(update_fields=['payment_id', 'status', 'updated_at'])
    return payment


def fetch_payment(payment_id: str) -> Optional[Payment]:
    if not payment_id:
        return None
    _ensure_configuration()
    return Payment.find_one(payment_id)


def update_order_status_from_payment(order: Order, payment: Payment) -> Order:
    status = getattr(payment, 'status', '')
    if status == 'succeeded':
        order.status = Order.STATUS_PAID
    elif status in {'canceled', 'canceled_by_merchant'}:
        order.status = Order.STATUS_CANCELED
    elif status in {'pending', 'waiting_for_capture'}:
        order.status = Order.STATUS_AWAITING
    else:
        order.status = Order.STATUS_FAILED
    order.save(update_fields=['status', 'updated_at'])
    return order
