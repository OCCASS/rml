from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy/<slug:slug>/', views.buy_product, name='buy_product'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('partnership/submit/', views.partnership_submit, name='partnership_submit'),
]
