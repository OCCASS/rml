from __future__ import annotations

from typing import Dict, List

from .services.cart import CartItem, get_cart


def cart(request) -> Dict[str, int | List[CartItem]]:
    cart_state = get_cart(request)
    return {
        'cart_items_count': cart_state.total_quantity,
        'cart_items': cart_state.items,
        'cart_total': cart_state.total_amount,
    }
