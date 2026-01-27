from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from store.forms import OrderDetailsForm, PartnershipForm
from store.models import Order, OrderItem, Product
from store.services import cart as cart_service
from store.services.notifications import notify_order_paid, notify_partnership
from store.services.payments import create_payment, fetch_payment, update_order_status_from_payment


def _is_ajax(request: HttpRequest) -> bool:
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _format_amount(amount: Decimal) -> str:
    return f'{amount:.0f}'


def _build_cart_payload(cart: cart_service.Cart, item: Optional[cart_service.CartItem] = None) -> dict:
    payload = {
        'cart': {
            'total_amount': _format_amount(cart.total_amount),
            'total_quantity': cart.total_quantity,
        },
        'is_empty': cart.total_quantity == 0,
    }
    if item:
        payload['item'] = {
            'product_id': item.product.id,
            'quantity': item.quantity,
            'total_price': _format_amount(item.total_price),
        }
    return payload


def index(request: HttpRequest) -> HttpResponse:
    products = Product.objects.prefetch_related('images').all()
    first_line_products = [product for product in products if product.first_line]
    second_line_products = [product for product in products if not product.first_line]
    return render(
        request,
        'store/index.html',
        {
            'first_line_products': first_line_products,
            'second_line_products': second_line_products,
            'partnership_form': PartnershipForm(),
        },
    )


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product.objects.prefetch_related('images'), slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})


def cart_view(request: HttpRequest) -> HttpResponse:
    cart = cart_service.get_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@require_POST
def add_to_cart(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    quantity = max(int(request.POST.get('quantity', 1)), 1)
    replace = request.POST.get('replace') == '1'
    cart = cart_service.add_to_cart(request, product.id, quantity, replace=replace)
    if _is_ajax(request):
        item = next((entry for entry in cart.items if entry.product.id == product.id), None)
        return JsonResponse(_build_cart_payload(cart, item=item))
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect(request.POST.get('next') or reverse('store:cart'))


@require_POST
def remove_from_cart(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    cart = cart_service.remove_from_cart(request, product.id)
    if _is_ajax(request):
        payload = _build_cart_payload(cart)
        payload['removed'] = True
        payload['product_id'] = product.id
        return JsonResponse(payload)
    messages.info(request, f'{product.name} убран из корзины')
    return redirect(reverse('store:cart'))


def _build_order_from_cart(cart: cart_service.Cart, metadata: Optional[dict] = None) -> Order:
    metadata = metadata or {}
    with transaction.atomic():
        order = Order.objects.create(
            total_amount=cart.total_amount,
            currency='RUB',
            metadata=metadata,
            cart_snapshot=cart_service.serialize_cart(cart),
        )
        for item in cart.items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
            )
    return order


def _start_payment_flow(request: HttpRequest, order: Order) -> HttpResponse:
    return_url = request.build_absolute_uri(reverse('store:payment_success'))
    description = f'Заказ #{order.id} в RML'
    try:
        payment = create_payment(order, return_url=return_url, description=description)
    except Exception as error:  # noqa: BLE001
        messages.error(request, f'Не удалось создать оплату: {error}')
        return redirect(reverse('store:cart'))
    request.session['last_payment_id'] = payment.id
    confirmation_url = getattr(payment.confirmation, 'confirmation_url', None)
    if confirmation_url:
        return redirect(confirmation_url)
    messages.error(request, 'Не удалось получить ссылку на оплату')
    return redirect(reverse('store:cart'))


def checkout(request: HttpRequest) -> HttpResponse:
    cart = cart_service.get_cart(request)
    if not cart.items:
        messages.error(request, 'Корзина пуста')
        return redirect(reverse('store:catalog'))
    return render(
        request,
        'store/checkout.html',
        {
            'cart': cart,
            'form': OrderDetailsForm(),
        },
    )


@require_POST
def checkout_submit(request: HttpRequest) -> HttpResponse:
    cart = cart_service.get_cart(request)
    if not cart.items:
        messages.error(request, 'Корзина пуста')
        return redirect(reverse('store:catalog'))
    form = OrderDetailsForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'store/checkout.html',
            {
                'cart': cart,
                'form': form,
            },
        )
    metadata = {
        'source': 'cart',
        'customer_name': form.cleaned_data['full_name'],
        'customer_phone': form.cleaned_data['phone'],
        'customer_address': form.cleaned_data['address'],
    }
    order = _build_order_from_cart(cart, metadata=metadata)
    return _start_payment_flow(request, order)


@require_POST
def buy_product(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    quantity = max(int(request.POST.get('quantity', 1)), 1)
    cart = cart_service.Cart(items=[cart_service.CartItem(product=product, quantity=quantity)])
    order = _build_order_from_cart(cart, metadata={'source': 'product', 'product_slug': product.slug})
    return _start_payment_flow(request, order)


def _resolve_payment_id(request: HttpRequest) -> Optional[str]:
    return request.GET.get('paymentId') or request.GET.get('payment_id') or request.session.get('last_payment_id')


def payment_success(request: HttpRequest) -> HttpResponse:
    payment_id = _resolve_payment_id(request)
    order = Order.objects.filter(payment_id=payment_id).first()
    payment: Optional[Any] = None
    if payment_id:
        try:
            payment = fetch_payment(payment_id)
        except Exception as error:  # noqa: BLE001
            messages.warning(request, f'Не удалось обновить статус оплаты: {error}')
    if payment and not order:
        metadata = getattr(payment, 'metadata', {}) or {}
        order_id = metadata.get('order_id') if hasattr(metadata, 'get') else None
        if order_id:
            order = Order.objects.filter(id=order_id).first()
    if payment and order:
        order = update_order_status_from_payment(order, payment)
        if order.status == Order.STATUS_PAID and not order.notified_at:
            notify_order_paid(order)
        cart_service.clear_cart(request)
    context = {
        'order': order,
        'payment_id': payment_id,
        'payment_status': getattr(payment, 'status', None),
    }
    return render(request, 'store/payment_success.html', context)


@require_POST
def partnership_submit(request: HttpRequest) -> HttpResponse:
    form = PartnershipForm(request.POST)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
                break
        return redirect(f"{reverse('store:catalog')}#partnership")
    notify_partnership(
        email=form.cleaned_data['email'],
        comment=form.cleaned_data.get('comment', ''),
    )
    messages.success(request, 'Спасибо! Мы получили заявку и свяжемся с вами.')
    return redirect(f"{reverse('store:catalog')}#partnership")

# Create your views here.
