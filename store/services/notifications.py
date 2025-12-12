from __future__ import annotations

import logging
from typing import Iterable

import requests
from django.conf import settings
from django.utils import timezone

from store.models import Order

logger = logging.getLogger(__name__)


def _send_telegram_message(token: str, chat_ids: Iterable[str], text: str) -> None:
    for chat_id in chat_ids:
        try:
            requests.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                timeout=5,
                data={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'},
            )
        except Exception:  # noqa: BLE001
            logger.exception('Failed to send Telegram notification for chat %s', chat_id)


def notify_order_paid(order: Order) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_IDS:
        return
    message = (
        f'Новый заказ #{order.id} оплачен.\n'
        f'Состав: {order.as_human_readable()}\n'
        f'Сумма: {order.total_amount:.2f} {order.currency}'
    )
    _send_telegram_message(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_IDS, message)
    order.notified_at = timezone.now()
    order.save(update_fields=['notified_at'])


def notify_partnership(email: str, comment: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_IDS:
        return
    text = f'Форма сотрудничества:\nEmail: {email}\nКомментарий: {comment or "—"}'
    _send_telegram_message(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_IDS, text)
