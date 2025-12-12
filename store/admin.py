from django.contrib import admin

from store.models import Order, OrderItem, Product, ProductImage

admin.site.site_header = 'RML — администрирование'
admin.site.site_title = 'RML — админ'
admin.site.index_title = 'Управление магазином'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'first_line', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'total_amount', 'payment_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment_id',)
    inlines = [OrderItemInline]

# Register your models here.
