# apps/store/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, SubCategory, Product,HomeSection,ShopReview
from .forms import SearchForm
from django.contrib.auth.decorators import login_required

def about_page(request):
    reviews = ShopReview.objects.filter(is_approved=True)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            text = request.POST.get('text')
            if text:
                ShopReview.objects.create(user=request.user, text=text)
                return redirect('store:about') # замените на ваш URL name
        else:
            return redirect('login') # или на страницу регистрации

    return render(request, 'pages/about.html', {'reviews': reviews})
def home(request):
    sections = HomeSection.objects.filter(is_active=True).prefetch_related(
        "products"
    )
    return render(request, "pages/home.html", {
        "sections": sections
    })

def section_detail(request, slug):
    section = get_object_or_404(
        HomeSection.objects.prefetch_related("products"),
        slug=slug,
        is_active=True
    )

    return render(request, "pages/section_detail.html", {
        "section": section,
        "products": section.products.filter(available=True),
    })

def product_list(request):
    form = SearchForm(request.GET or None)
    products = Product.objects.filter(available=True).order_by("id")

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
    return render(request, "store/product_detail.html", {
        "product": product
    })


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()
    products = Product.objects.filter(category__in=subcategories, available=True)

    return render(request, "store/category.html", {
        "category": category,
        "products": products,
        "subcategories": subcategories,
    })


def subcategory_view(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = Product.objects.filter(category=subcategory, available=True)

    return render(request, "store/subcategory.html", {
        "subcategory": subcategory,
        "products": products,
    })


def faq(request):
    return render(request, "pages/faq.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")

def contacts_page(request):
    return render(request, 'pages/contacts.html')
