# store/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.db.models import Q,Count,Case, When, IntegerField,Sum,DecimalField,ExpressionWrapper,F
from .models import *
from .forms import SearchForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from .forms import ProductForm, CategoryForm, SubCategoryForm, HomeSectionForm
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from cart.cart import Cart
from django.views.decorators.http import require_POST
from .chat_service import (
    ask_gigachat,
    extract_budget,
    get_products_for_budget,
    find_products_by_text,
    get_gift_set
)
import traceback
from django.shortcuts import render
from orders.models import Order
from store.models import Product, ShopReview
from users.models import CustomUser
from django.db.models.functions import TruncDate

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

# HOME
def home(request):
    sections = HomeSection.objects.filter(
        is_active=True
    ).prefetch_related("products")

    return render(request, "pages/home.html", {
        "sections": sections
    })


# SECTION DETAIL
def section_detail(request, slug):
    section = get_object_or_404(
        HomeSection.objects.prefetch_related("products"),
        slug=slug,
        is_active=True
    )

    products = section.products.filter(
        stock__gt=0
    ).order_by("id")

    return render(request, "pages/section_detail.html", {
        "section": section,
        "products": products,
    })


# PRODUCT LIST
def product_list(request):
    form = SearchForm(request.GET or None)

    products = Product.objects.filter(
        stock__gt=0
    ).order_by("id")

    if form.is_valid():
        q = form.cleaned_data.get("q")

        if q:
            products = products.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
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
        Product.objects.filter(stock__gt=0),
        Q(slug__iexact=slug)
    )

    return render(request, "store/product_detail.html", {
        "product": product
    })


# CATEGORY
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)

    subcategories = category.subcategories.annotate(
        available_products_count=Count(
            "products",
            filter=Q(products__stock__gt=0)
        )
    )

    products = Product.objects.filter(
        category__in=subcategories,
        stock__gt=0
    )

    return render(request, "store/category.html", {
        "category": category,
        "subcategories": subcategories,
        "products": products,
    })

# SUBCATEGORY
def subcategory_view(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)

    subcategories = SubCategory.objects.filter(
        category=subcategory.category
    ).annotate(
        available_products_count=Count(
            "products",
            filter=Q(products__stock__gt=0)
        )
    )

    products = Product.objects.filter(
        category=subcategory,
        stock__gt=0
    )

    return render(request, "store/subcategory.html", {
        "subcategory": subcategory,
        "subcategories": subcategories,
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


def admin_statistics(request):

    # --- ORDERS ---
    orders = Order.objects.all()

    total_orders = orders.count()

    total_revenue = sum(o.total_price for o in orders)
    total_final_revenue = sum(o.final_total_price for o in orders)

    paid_orders = orders.filter(status="paid").count()
    delivered_orders = orders.filter(status="delivered").count()
    processing_orders = orders.filter(status="processing").count()

    total_bonus_used = sum(o.bonus_used for o in orders)

    # --- 📈 SALES BY DAY (БЕЗ ORM — СТАБИЛЬНО) ---
    sales_by_day = {}

    for order in orders:
        day = order.created_at.date()
        sales_by_day[day] = sales_by_day.get(day, 0) + float(order.final_total_price)

    sorted_days = sorted(sales_by_day.keys())

    dates = [d.strftime("%d.%m.%Y") for d in sorted_days]
    sales = [sales_by_day[d] for d in sorted_days]

    # --- USERS ---
    total_users = CustomUser.objects.count()
    users_with_bonus = CustomUser.objects.filter(bonus_points__gt=0).count()

    # --- PRODUCTS ---
    total_products = Product.objects.count()
    active_products = Product.objects.filter(available=True).count()
    out_of_stock = sum(1 for p in Product.objects.all() if p.is_out_of_stock)

    # --- REVIEWS ---
    total_reviews = ShopReview.objects.count()
    approved_reviews = ShopReview.objects.filter(is_approved=True).count()
    pending_reviews = ShopReview.objects.filter(is_approved=False).count()

    # --- LAST ORDERS ---
    last_orders = Order.objects.order_by("-created_at")[:10]

    return render(request, "store/admin/statistics.html", {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_final_revenue": total_final_revenue,

        "paid_orders": paid_orders,
        "delivered_orders": delivered_orders,
        "processing_orders": processing_orders,

        "total_bonus_used": total_bonus_used,

        "total_users": total_users,
        "users_with_bonus": users_with_bonus,

        "total_products": total_products,
        "active_products": active_products,
        "out_of_stock": out_of_stock,

        "total_reviews": total_reviews,
        "approved_reviews": approved_reviews,
        "pending_reviews": pending_reviews,

        "last_orders": last_orders,

        # 📊 chart data
        "dates": dates,
        "sales": sales,
    })

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

# =========================
# 🤖 AI CHAT
# =========================

@login_required
@require_POST
def clear_chat(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return JsonResponse({"success": True})

@login_required
def chat_history(request):
    messages = ChatMessage.objects.filter(
        user=request.user
    ).order_by("created_at")[:50]

    history = []

    for msg in messages:

        # 👉 сообщение пользователя
        history.append({
            "type": "user",
            "text": msg.message
        })

        # 👉 если структурированный ответ (товары)
        if msg.reply_json:
            history.append({
                "type": "structured",
                "data": msg.reply_json
            })

        # 👉 обычный текст
        elif msg.reply_text:
            history.append({
                "type": "bot",
                "text": msg.reply_text
            })

    return JsonResponse({"history": history})

from .chat_service import (
    ask_gigachat,
    extract_budget,
    get_products_for_budget,
    find_products_by_text,
    get_gift_set
)

@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        # ✅ безопасный парсинг
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({"reply": "Ошибка запроса"}, status=400)

        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"reply": "✍️ Напиши вопрос"})

        print(f"🤖 USER: {message}")

        # =========================
        # 🎯 1. БЮДЖЕТ
        # =========================
        budget = extract_budget(message)

        if budget:
            items, total = get_products_for_budget(budget)

            if items:
                response = {
                    "mode": "budget",
                    "message": f"🎯 Подбор на {budget}₽ (~{total}₽)",
                    "items": items
                }
            else:
                response = {
                    "reply": "😔 Не удалось подобрать товары под бюджет"
                }

            save_chat(request, message, response)
            return JsonResponse(response)

        # =========================
        # 🎁 2. ПОДАРОК
        # =========================
        if "подар" in message.lower():
            items = get_gift_set()

            if items:
                response = {
                    "mode": "gift",
                    "message": "🎁 Подарочный набор:",
                    "items": items
                }
            else:
                response = {
                    "reply": "😔 Нет готовых подарочных наборов"
                }

            save_chat(request, message, response)
            return JsonResponse(response)
        # =========================
        # 🔥 СКИДКИ
        # =========================

        discount_words = [
            "скидк",
            "акци",
            "дешев",
            "выгод",
            "распродаж"
        ]

        if any(word in message.lower() for word in discount_words):

            items = get_discount_products()

            if items:

                response = {

                    "mode": "discounts",

                    "message": "🔥 Товары со скидками:",

                    "items": items
                }

            else:

                response = {
                    "reply": "😔 Сейчас нет товаров со скидкой"
                }

            save_chat(request, message, response)

            return JsonResponse(response)

        # =========================
        # 🛒 3. СБОР ИЗ ТЕКСТА
        # =========================
        items = find_products_by_text(message)

        if items:
            response = {
                "mode": "cart_builder",
                "message": "🛒 Нашёл товары:",
                "items": items
            }

            save_chat(request, message, response)
            return JsonResponse(response)

        # =========================
        # 🤖 4. GIGACHAT (fallback)
        # =========================
        reply = ask_gigachat(message)

        response = {
            "reply": reply or "🤖 Не смог ответить"
        }

        save_chat(request, message, response)
        return JsonResponse(response)

    except Exception as e:
        print("💥 AI CHAT ERROR:")
        traceback.print_exc()

        return JsonResponse({
            "reply": "❌ Ошибка сервера. Попробуй позже."
        }, status=500)

def save_chat(request, message, response):
    """
    Сохраняет историю чата (и текст, и JSON)
    """

    if not request.user.is_authenticated:
        return

    try:
        ChatMessage.objects.create(
            user=request.user,
            message=message,

            # если обычный ответ
            reply_text=response.get("reply"),

            # если есть режим (товары, бюджет и т.д.)
            reply_json=response if "mode" in response else None
        )

    except Exception as e:
        print("CHAT SAVE ERROR:", e)

# ================= ADD TO CART =================
@csrf_exempt
@require_POST
def ai_add_to_cart(request):
    try:
        data = json.loads(request.body)
        slug = data.get("slug")

        product = Product.objects.filter(slug=slug, available=True).first()

        if not product:
            return JsonResponse({"error": "Нет товара"}, status=404)

        cart = Cart(request)

        current = cart.get_product_quantity(product)

        if current >= product.stock:
            return JsonResponse({"error": "Нет в наличии"}, status=400)

        if current + 1 > 10:
            return JsonResponse({"error": "Лимит 10"}, status=400)

        cart.add(product, quantity=1)

        return JsonResponse({
            "success": True,
            "cart_count": len(cart),
            "cart_total": float(cart.get_total_price())
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ================= BULK ADD =================
@csrf_exempt
@require_POST
def ai_bulk_add_to_cart(request):
    try:
        data = json.loads(request.body)
        items = data.get("items", [])

        cart = Cart(request)

        added = []
        errors = []

        for item in items:
            slug = item.get("slug")
            qty = int(item.get("quantity", 1))

            product = Product.objects.filter(slug=slug, available=True).first()

            if not product:
                errors.append(slug)
                continue

            current = cart.get_product_quantity(product)

            if current + qty > product.stock:
                errors.append(product.name)
                continue

            cart.add(product, quantity=qty)

            added.append(product.name)

        return JsonResponse({
            "success": True,
            "added": added,
            "errors": errors,
            "cart_count": len(cart),
            "cart_total": float(cart.get_total_price())
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ================= СКИДКИ =================

def get_discount_products():

    from .models import Product

    products = Product.objects.filter(
        available=True,
        stock__gt=0,
        discount_percent__gt=0
    ).order_by("-discount_percent")[:10]

    result = []

    for p in products:

        result.append({
            "slug": p.slug,
            "name": p.name,

            # старая цена
            "old_price": float(p.old_price),

            # новая цена
            "price": float(p.final_price),

            "discount_percent": p.discount_percent,

            "quantity": 1
        })

    return result