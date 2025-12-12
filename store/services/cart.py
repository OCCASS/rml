from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List

from django.conf import settings

from store.models import Product


@dataclass
class CartItem:
    product: Product
    quantity: int

    @property
    def total_price(self) -> Decimal:
        return self.product.price * self.quantity


@dataclass
class Cart:
    items: List[CartItem]

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def total_amount(self) -> Decimal:
        return sum((item.total_price for item in self.items), Decimal('0.00'))


def _get_session_cart(request) -> Dict[str, int]:
    return dict(request.session.get(settings.CART_SESSION_KEY, {}))


def _persist_session_cart(request, cart_data: Dict[str, int]) -> None:
    request.session[settings.CART_SESSION_KEY] = cart_data
    request.session.modified = True


def get_cart(request) -> Cart:
    cart_data = _get_session_cart(request)
    products = Product.objects.filter(id__in=cart_data.keys()).prefetch_related('images')
    product_map = {str(product.id): product for product in products}
    items: List[CartItem] = []
    for product_id, quantity in cart_data.items():
        product = product_map.get(str(product_id))
        if not product:
            continue
        items.append(CartItem(product=product, quantity=quantity))
    return Cart(items=items)


def add_to_cart(request, product_id: int, quantity: int = 1, replace: bool = False) -> Cart:
    cart_data = _get_session_cart(request)
    current = cart_data.get(str(product_id), 0)
    cart_data[str(product_id)] = quantity if replace else current + quantity
    _persist_session_cart(request, cart_data)
    return get_cart(request)


def remove_from_cart(request, product_id: int) -> Cart:
    cart_data = _get_session_cart(request)
    cart_data.pop(str(product_id), None)
    _persist_session_cart(request, cart_data)
    return get_cart(request)


def clear_cart(request) -> None:
    if settings.CART_SESSION_KEY in request.session:
        del request.session[settings.CART_SESSION_KEY]
        request.session.modified = True


def serialize_cart(cart: Cart) -> List[dict]:
    return [
        {
            'product_id': item.product.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'unit_price': str(item.product.price),
        }
        for item in cart.items
    ]
