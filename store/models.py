# store/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings
from PIL import Image
from django.contrib.auth.models import User
from decimal import Decimal
def product_image_upload_to(instance, filename):
    return f"products/{instance.category.slug if instance.category else 'misc'}/{filename}"


class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", max_length=120, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:category_detail", args=[self.slug])


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="subcategories",
        on_delete=models.CASCADE
    )
    name = models.CharField("Название подкатегории", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return f"{self.category.name} → {self.name}"

    def get_absolute_url(self):
        return reverse("store:subcategory", args=[self.slug])

class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True)

    category = models.ForeignKey(
        "SubCategory",
        on_delete=models.CASCADE,
        related_name="products"
    )

    description = models.TextField("Описание", blank=True)

    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField("Скидка (%)", default=0)

    stock = models.PositiveIntegerField("Количество", default=0)
    weight = models.PositiveIntegerField("Вес (г)", default=0)

    image = models.ImageField(upload_to="products/", blank=True, null=True)

    available = models.BooleanField("Доступен", default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    @property
    def is_discount(self):
        return self.discount_percent > 0

    @property
    def old_price(self):
        return self.price

    @property
    def final_price(self):
        if self.discount_percent:
            return round(self.price * (100 - self.discount_percent) / 100, 2)
        return self.price

    @property
    def is_out_of_stock(self):
        return self.stock <= 0 or not self.available

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])
    
class HomeSection(models.Model):
    title = models.CharField("Заголовок секции", max_length=120)
    slug = models.SlugField(unique=True)

    products = models.ManyToManyField(
        Product,
        verbose_name="Товары",
        blank=True
    )

    image = models.ImageField(
        "Баннер (картинка)",
        upload_to="sections/",
        blank=True,
        null=True
    )

    link_section = models.ForeignKey(
        "self",
        verbose_name="Ссылка на секцию",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="linked_from"
    )

    is_active = models.BooleanField("Активна", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Секция главной"
        verbose_name_plural = "Секции главной"

    def __str__(self):
        return self.title

class ShopReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено админом")

    class Meta:
        verbose_name = "Отзыв о магазине"
        verbose_name_plural = "Отзывы о магазине"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username}"

class ReviewReaction(models.Model):
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = (
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(
        ShopReview,
        on_delete=models.CASCADE,
        related_name="reactions"
    )
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    
    @property
    def likes_count(self):
        return self.reactions.filter(value=1).count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(value=-1).count()

    class Meta:
        unique_together = ("user", "review")


class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )

    # сообщение пользователя
    message = models.TextField()

    # обычный текстовый ответ
    reply_text = models.TextField(blank=True, null=True)

    # структурированный ответ (товары, режимы)
    reply_json = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.message[:30]}"