# store/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.db.models import Q,Count,Case, When, IntegerField
from .models import Category, SubCategory, Product,HomeSection,ShopReview,ReviewReaction
from .forms import SearchForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from .forms import ProductForm, CategoryForm, SubCategoryForm, HomeSectionForm
from django.http import JsonResponse

def about_page(request):
    reviews = ShopReview.objects.filter(is_approved=True).annotate(
        likes_count=Count('reactions', filter=Q(reactions__value=1)),
        dislikes_count=Count('reactions', filter=Q(reactions__value=-1)),
    ).select_related('user')

    # 👉 Добавляем реакцию пользователя
    if request.user.is_authenticated:
        user_reactions = ReviewReaction.objects.filter(
            user=request.user,
            review__in=reviews
        )

        reaction_map = {r.review_id: r.value for r in user_reactions}

        for review in reviews:
            review.user_reaction = reaction_map.get(review.id, 0)
    else:
        for review in reviews:
            review.user_reaction = 0

    # POST (отзыв)
    if request.method == 'POST':
        if request.user.is_authenticated:
            text = request.POST.get('text')
            if text:
                ShopReview.objects.create(
                    user=request.user,
                    text=text,
                    is_approved=False
                )
                return redirect('store:about')
        else:
            return redirect('users:login')

    return render(request, 'pages/about.html', {
        'reviews': reviews
    })

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

    products = section.products.filter(
    ).annotate(
        in_stock_order=Case(
            When(stock__lte=0, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by("in_stock_order", "id")

    return render(request, "pages/section_detail.html", {
        "section": section,
        "products": products,
    })


# PRODUCT LIST
def product_list(request):
    form = SearchForm(request.GET or None)

    products = Product.objects.filter(
    ).annotate(
        in_stock_order=Case(
            When(stock__lte=0, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by("in_stock_order", "id")

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


# PRODUCT DETAIL
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.all(),
        Q(slug__iexact=slug)
    )

    return render(request, "store/product_detail.html", {
        "product": product
    })


# CATEGORY
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()

    products = Product.objects.filter(
        category__in=subcategories,
    ).annotate(
        in_stock_order=Case(
            When(stock__lte=0, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by("in_stock_order", "id")

    return render(request, "store/category.html", {
        "category": category,
        "products": products,
        "subcategories": subcategories,
    })


# SUBCATEGORY
def subcategory_view(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)

    products = Product.objects.filter(
        category=subcategory,
    ).annotate(
        in_stock_order=Case(
            When(stock__lte=0, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by("in_stock_order", "id")

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

##Админка
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='users:login')(view_func)

@staff_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

# ТОВАРЫ
@staff_required
def admin_products(request):
    products = Product.objects.all().order_by('-id')
    return render(request, "store/admin/products.html", {"products": products})

@staff_required
def admin_add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар добавлен")
            return redirect("store:admin_products")
    else:
        form = ProductForm()
    return render(request, "store/admin/product_form.html", {"form": form, "title": "Добавить товар"})

@staff_required
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар обновлён")
            return redirect("store:admin_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "store/admin/product_form.html", {"form": form, "title": "Редактировать товар"})

@staff_required
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Товар удалён")
    return redirect("store:admin_products")

# КАТЕГОРИИ
@staff_required
def admin_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, "store/admin/categories.html", {"categories": categories})

@staff_required
def admin_add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория добавлена")
            return redirect("store:admin_categories")
    else:
        form = CategoryForm()
    return render(request, "store/admin/category_form.html", {"form": form, "title": "Добавить категорию"})

@staff_required
def admin_edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория обновлена")
            return redirect("store:admin_categories")
    else:
        form = CategoryForm(instance=category)
    return render(request, "store/admin/category_form.html", {"form": form, "title": "Редактировать категорию"})

@staff_required
def admin_delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Категория удалена")
    return redirect("store:admin_categories")

# ПОДКАТЕГОРИИ
@staff_required
def admin_subcategories(request):
    subcategories = SubCategory.objects.all().order_by('category__name', 'name')
    return render(request, "store/admin/subcategories.html", {"subcategories": subcategories})

@staff_required
def admin_add_subcategory(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Подкатегория добавлена")
            return redirect("store:admin_subcategories")
    else:
        form = SubCategoryForm()
    return render(request, "store/admin/subcategory_form.html", {"form": form, "title": "Добавить подкатегорию"})

@staff_required
def admin_edit_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == "POST":
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, "Подкатегория обновлена")
            return redirect("store:admin_subcategories")
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, "store/admin/subcategory_form.html", {"form": form, "title": "Редактировать подкатегорию"})

@staff_required
def admin_delete_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    subcategory.delete()
    messages.success(request, "Подкатегория удалена")
    return redirect("store:admin_subcategories")

# СЕКЦИИ ГЛАВНОЙ

@staff_required
def admin_sections(request):
    sections = HomeSection.objects.all().order_by('order')
    return render(request, "store/admin/sections.html", {"sections": sections})

@staff_required
def admin_add_section(request):
    if request.method == "POST":
        form = HomeSectionForm(request.POST, request.FILES)  # 👈 ВАЖНО
        if form.is_valid():
            form.save()
            messages.success(request, "Секция добавлена")
            return redirect("store:admin_sections")
    else:
        form = HomeSectionForm()

    return render(request, "store/admin/section_form.html", {
        "form": form,
        "title": "Добавить секцию"
    })

@staff_required
def admin_edit_section(request, pk):
    section = get_object_or_404(HomeSection, pk=pk)

    if request.method == "POST":
        form = HomeSectionForm(request.POST, request.FILES, instance=section)  # 👈 ВАЖНО
        if form.is_valid():
            form.save()
            messages.success(request, "Секция обновлена")
            return redirect("store:admin_sections")
    else:
        form = HomeSectionForm(instance=section)

    return render(request, "store/admin/section_form.html", {
        "form": form,
        "title": "Редактировать секцию"
    })

@staff_required
def admin_delete_section(request, pk):
    section = get_object_or_404(HomeSection, pk=pk)
    section.delete()
    messages.success(request, "Секция удалена")
    return redirect("store:admin_sections")

# ОТЗЫВЫ
@staff_required
def admin_reviews(request):
    reviews = ShopReview.objects.all().order_by('-created_at')
    return render(request, "store/admin/reviews.html", {"reviews": reviews})

@staff_required
def admin_approve_review(request, pk):
    review = get_object_or_404(ShopReview, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, "Отзыв одобрен")
    return redirect("store:admin_reviews")

@staff_required
def admin_delete_review(request, pk):
    review = get_object_or_404(ShopReview, pk=pk)
    review.delete()
    messages.success(request, "Отзыв удалён")
    return redirect("store:admin_reviews")


@login_required
def toggle_reaction(request, review_id):
    review = get_object_or_404(ShopReview, id=review_id)
    value = int(request.POST.get("value"))

    reaction, created = ReviewReaction.objects.get_or_create(
        user=request.user,
        review=review,
        defaults={"value": value}
    )

    if not created:
        if reaction.value == value:
            reaction.delete()
        else:
            reaction.value = value
            reaction.save()

    likes = review.reactions.filter(value=1).count()
    dislikes = review.reactions.filter(value=-1).count()

    user_reaction = 0
    if request.user.is_authenticated:
        r = ReviewReaction.objects.filter(user=request.user, review=review).first()
        if r:
            user_reaction = r.value

    return JsonResponse({
        "likes": likes,
        "dislikes": dislikes,
        "user_reaction": user_reaction
    })