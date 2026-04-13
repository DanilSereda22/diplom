# store/models.py
from django.db import models
from django.urls import reverse
from django.db import models
from django.conf import settings

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


from django.db import models
from django.urls import reverse

class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, db_index=True)

    category = models.ForeignKey(
        "SubCategory",
        on_delete=models.CASCADE,
        related_name="products"
    )

    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField("Количество на складе", default=0)
    weight = models.PositiveIntegerField("Вес (г)", default=0)

    image = models.ImageField(upload_to="products/", blank=True, null=True)

    available = models.BooleanField("Доступен", default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    @property
    def is_out_of_stock(self):
        return self.stock <= 0 or not self.available

    def save(self, *args, **kwargs):
        # Авто-логика наличия
        if self.stock <= 0:
            self.available = False
        super().save(*args, **kwargs)
    
class HomeSection(models.Model):
    title = models.CharField("Заголовок секции", max_length=120)
    slug = models.SlugField(unique=True)
    products = models.ManyToManyField(
        Product,
        verbose_name="Товары",
        blank=True
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

class ShopReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}"


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