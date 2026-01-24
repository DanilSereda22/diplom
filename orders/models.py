from django.db import models
from django.conf import settings
from store.models import Product

class Order(models.Model):
    DELIVERY_CHOICES = (
        ("pickup", "Самовывоз"),
        ("delivery", "Доставка"),
    )

    STATUS_CHOICES = (
        ("processing", "В обработке"),
        ("paid", "Оплачен"),
        ("delivered", "Доставлен"),
    )
    @property
    def total_price(self):
        return sum(
            item.price * item.quantity
            for item in self.items.all()
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES
    )

    delivery_address = models.CharField(
        "Адрес доставки",
        max_length=255,
        blank=True
    )

    delivery_comment = models.TextField(
        "Комментарий к доставке",
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing"
    )

    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self):
        return self.price * self.quantity
