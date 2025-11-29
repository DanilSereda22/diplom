# apps/store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),

    # Категории
    path("category/<slug:slug>/", views.category_view, name="category"),

    # Подкатегории
    path("subcategory/<slug:slug>/", views.subcategory_view, name="subcategory"),

    # Товар
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
