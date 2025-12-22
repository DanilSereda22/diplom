# apps/store/models.py
from django.db import models
from django.urls import reverse


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
        # ✅ ИСПРАВЛЕНО
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
        # ✅ ИСПРАВЛЕНО (совпадает с urls.py)
        return reverse("store:subcategory", args=[self.slug])


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True)
    category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Количество на складе", default=0)
    weight = models.PositiveIntegerField("Вес (г)", default=0)
    image = models.ImageField(upload_to=product_image_upload_to, blank=True, null=True)
    available = models.BooleanField("Доступен", default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])
