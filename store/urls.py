# apps/store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("subcategory/<slug:slug>/", views.subcategory_view, name="subcategory"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
