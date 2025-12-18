# apps/store/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, SubCategory, Product
from .forms import SearchForm

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcats = category.subcategories.all()
    products = Product.objects.filter(category__in=subcats, available=True)
    return render(request, "store/category.html", {
        "category": category,
        "products": products,
        "subcategories": subcats,
    })

def subcategory_view(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = Product.objects.filter(category=subcategory, available=True)
    return render(request, "store/subcategory.html", {
        "subcategory": subcategory,
        "products": products
    })

def product_list(request):
    form = SearchForm(request.GET or None)
    products = Product.objects.filter(available=True)
    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            products = products.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)
    return render(request, "store/product_list.html", {
        "products": products,
        "form": form,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, "store/product_detail.html", {"product": product})

def delivery(request):
    return render(request, "pages/delivery.html")

def faq(request):
    return render(request, "pages/faq.html")

def privacy(request):
    return render(request, "pages/privacy.html")

def terms(request):
    return render(request, "pages/terms.html")

