# apps/store/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

def product_image_upload_to(instance, filename):
    return f"products/{instance.category.slug if instance.category else 'misc'}/{filename}"

class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:category_detail", args=[self.slug])

class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    weight = models.PositiveIntegerField("Вес(г)", default=0)
    image = models.ImageField("Изображение", upload_to=product_image_upload_to, blank=True, null=True)
    available = models.BooleanField("Доступен", default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])
