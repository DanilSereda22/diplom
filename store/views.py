# apps/store/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product
from .forms import SearchForm
from django.db import models
from django.db.models import Q

def index(request):
    categories = Category.objects.all()
    popular = Product.objects.filter(available=True).order_by("-created")[:8]
    context = {"categories": categories, "popular": popular}
    return render(request, "index.html", context)

def product_list(request, category_slug=None):
    form = SearchForm(request.GET or None)
    qs = Product.objects.filter(available=True)
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        qs = qs.filter(category=category)
    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            qs = qs.filter(models.Q(name__icontains=q) | models.Q(description__icontains=q))
    paginator = Paginator(qs, 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)
    return render(request, "store/product_list.html", {"products": products, "category": category, "form": form})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, "store/product_detail.html", {"product": product})
