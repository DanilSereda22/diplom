# orders/models.py
from django.db import models
from django.conf import settings
from store.models import Product
from decimal import Decimal

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

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    delivery_address = models.CharField(max_length=255, blank=True)
    delivery_comment = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
    bonus_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_price(self):
        """Сумма всех товаров без учета бонусов"""
        return sum(item.total_price for item in self.items.all())

    @property
    def final_total_price(self):
        """Сумма с учетом списанных бонусов"""
        return max(Decimal(0), self.total_price - self.bonus_used)

    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
