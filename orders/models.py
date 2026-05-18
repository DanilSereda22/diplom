from django.db import models
from django.conf import settings
from store.models import Product
from decimal import Decimal
from django.db.models import Max
from django.db import transaction


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
        on_delete=models.CASCADE,
        related_name="orders"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    delivery_address = models.CharField(max_length=255, blank=True)

    delivery_comment = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    bonus_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # 🔥 НОВОЕ ПОЛЕ (красивый номер заказа)
    order_number = models.PositiveIntegerField(
        unique=True,
        editable=False,
        null=True,
        blank=True
    )

    @property
    def total_price(self):
        """Сумма всех товаров без учета бонусов"""
        return sum(item.total_price for item in self.items.all())

    @property
    def final_total_price(self):
        """Сумма с учетом списанных бонусов"""
        return max(Decimal(0), self.total_price - self.bonus_used)

    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.db import transaction

            with transaction.atomic():
                existing = set(
                    Order.objects.values_list("order_number", flat=True)
                )

                i = 1
                while i in existing:
                    i += 1

                self.order_number = i

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.order_number} ({self.get_status_display()})"


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