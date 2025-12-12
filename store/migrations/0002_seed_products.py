from decimal import Decimal

from django.db import migrations


def seed_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    ProductImage = apps.get_model('store', 'ProductImage')
    products = [
        {
            'name': 'Болеро “Темно-коричневый”',
            'slug': 'bolero-dark',
            'price': Decimal('7990'),
            'first_line': True,
            'description': 'Многофункциональное болеро-трансформер, которое можно носить на плечах, как объемный воротник или шарф.',
            'details': [
                'Материал: искусственный мех кролика',
                'Подкладка: атлас с вискозой',
                'Ремешок: натуральная кожа',
                'Длина ремешка: 114-139 см',
                'Цвет: темно-коричневый',
            ],
            'images': [
                ('images/catalog1.jpg', 'Болеро темно-коричневый — общий вид'),
                ('images/catalog2.jpeg', 'Болеро темно-коричневый — детали'),
                ('images/catalog3.jpg', 'Болеро темно-коричневый — на модели'),
            ],
        },
        {
            'name': 'Болеро “Песок”',
            'slug': 'bolero-sand',
            'price': Decimal('8990'),
            'first_line': True,
            'description': 'Теплое болеро с мягким мехом и регулируемым кожаным ремешком.',
            'details': [
                'Материал: искусственный мех кролика',
                'Подкладка: атлас с вискозой',
                'Ремешок: натуральная кожа',
                'Длина ремешка: 114-139 см',
                'Цвет: песочный',
            ],
            'images': [
                ('images/catalog2.jpeg', 'Болеро песок — общий вид'),
                ('images/catalog1.jpg', 'Болеро песок — детали'),
                ('images/catalog4.jpg', 'Болеро песок — на модели'),
            ],
        },
        {
            'name': 'Болеро “Карамель”',
            'slug': 'bolero-caramel',
            'price': Decimal('8990'),
            'first_line': True,
            'description': 'Легкое карамельное болеро с акцентом на фактурный мех и плотную посадку.',
            'details': [
                'Материал: искусственный мех кролика',
                'Подкладка: атлас с вискозой',
                'Ремешок: натуральная кожа',
                'Длина ремешка: 114-139 см',
                'Цвет: карамель',
            ],
            'images': [
                ('images/catalog3.jpg', 'Болеро карамель — общий вид'),
                ('images/catalog1.jpg', 'Болеро карамель — детали'),
                ('images/catalog5.jpeg', 'Болеро карамель — на модели'),
            ],
        },
        {
            'name': 'Шарф “ЧБ”',
            'slug': 'scarf-bw',
            'price': Decimal('3590'),
            'first_line': False,
            'description': 'Контрастный шарф с бархатистой текстурой и кожаным ремешком.',
            'details': [
                'Материал: искусственный мех кролика',
                'Подкладка: хлопок с вискозой',
                'Ремешок: натуральная кожа',
                'Ширина: 11 см',
                'Цвет: черно-белый',
            ],
            'images': [
                ('images/catalog4.jpg', 'Шарф ЧБ — общий вид'),
                ('images/catalog2.jpeg', 'Шарф ЧБ — детали'),
                ('images/catalog3.jpg', 'Шарф ЧБ — на модели'),
            ],
        },
        {
            'name': 'Шарф “Розовый”',
            'slug': 'scarf-pink',
            'price': Decimal('3590'),
            'first_line': False,
            'description': 'Мягкий розовый шарф-трансформер, который можно носить как воротник или в полный рост.',
            'details': [
                'Материал: искусственный мех кролика',
                'Подкладка: атлас с вискозой',
                'Ремешок: натуральная кожа',
                'Ширина: 11 см',
                'Цвет: розовый',
            ],
            'images': [
                ('images/catalog5.jpeg', 'Шарф розовый — общий вид'),
                ('images/catalog2.jpeg', 'Шарф розовый — детали'),
                ('images/catalog4.jpg', 'Шарф розовый — на модели'),
            ],
        },
    ]
    for product_data in products:
        images = product_data.pop('images', [])
        product = Product.objects.create(**product_data)
        for sort_order, (path, alt) in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image_path=path,
                alt_text=alt,
                sort_order=sort_order,
            )


def remove_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Product.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_products),
    ]
