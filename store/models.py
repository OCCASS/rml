from decimal import Decimal

from django.db import models
from django.urls import reverse


class Product(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    details = models.JSONField('Детали', default=list, blank=True)
    first_line = models.BooleanField('Первая линия', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-first_line', 'id']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('store:product_detail', args=[self.slug])

    def main_image(self):
        return self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='Товар')
    image_path = models.CharField('Путь к изображению', max_length=255)
    alt_text = models.CharField('Описание', max_length=255, blank=True)
    sort_order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self) -> str:
        return f'{self.product.name} — {self.alt_text or self.image_path}'


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_AWAITING = 'awaiting_confirmation'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Создан'),
        (STATUS_AWAITING, 'Ожидает подтверждения'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_FAILED, 'Ошибка'),
        (STATUS_CANCELED, 'Отменен'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField('Статус', max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_id = models.CharField('ID платежа', max_length=128, blank=True, db_index=True)
    total_amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField('Валюта', max_length=3, default='RUB')
    metadata = models.JSONField('Метаданные', default=dict, blank=True)
    notified_at = models.DateTimeField('Уведомлено продавцов', null=True, blank=True)
    cart_snapshot = models.JSONField('Состав заказа (слепок)', default=list, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self) -> str:
        return f'Order #{self.pk or "draft"} — {self.status}'

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.save(update_fields=['status', 'updated_at'])

    def as_human_readable(self) -> str:
        lines = []
        for item in self.items.all():
            lines.append(f'{item.product_name} x{item.quantity} — {item.line_total:.2f} {self.currency}')
        return '; '.join(lines)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Товар')
    product_name = models.CharField('Название товара', max_length=255)
    unit_price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        ordering = ['id']
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self) -> str:
        return f'{self.product_name} x{self.quantity}'

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

# Create your models here.
