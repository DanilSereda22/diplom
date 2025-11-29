# apps/store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="category_detail"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
