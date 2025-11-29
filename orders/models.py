# apps/orders/models.py
from django.db import models
from django.conf import settings
from store.models import Product

class Order(models.Model):
    DELIVERY_CHOICES = [
        ("courier", "Курьер"),
        ("pickup", "Самовывоз"),
    ]
    STATUS_CHOICES = [
        ("paid", "Оплачен"),
        ("processing", "В обработке"),
        ("delivered", "Доставлен"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=30)
    address = models.TextField("Адрес доставки")
    delivery_method = models.CharField("Метод доставки", max_length=20, choices=DELIVERY_CHOICES)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order #{self.pk} by {self.first_name} {self.last_name}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

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
