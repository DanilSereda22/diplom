# apps/store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("section/<slug:slug>/", views.section_detail, name="section_detail"),
    path("catalog/", views.product_list, name="product_list"),
    path("category/<slug:slug>/", views.category_view, name="category_detail"),
    path("subcategory/<slug:slug>/", views.subcategory_view, name="subcategory"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("review/<int:review_id>/react/", views.toggle_reaction, name="review_react"),
    
    path('contacts/', views.contacts_page, name='contacts'),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("about/", views.about_page, name="about"),

    # админка
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/products/", views.admin_products, name="admin_products"),
    path("admin/products/add/", views.admin_add_product, name="admin_add_product"),
    path("admin/products/<int:pk>/edit/", views.admin_edit_product, name="admin_edit_product"),
    path("admin/products/<int:pk>/delete/", views.admin_delete_product, name="admin_delete_product"),

    path("admin/categories/", views.admin_categories, name="admin_categories"),
    path("admin/categories/add/", views.admin_add_category, name="admin_add_category"),
    path("admin/categories/<int:pk>/edit/", views.admin_edit_category, name="admin_edit_category"),
    path("admin/categories/<int:pk>/delete/", views.admin_delete_category, name="admin_delete_category"),

    path("admin/subcategories/", views.admin_subcategories, name="admin_subcategories"),
    path("admin/subcategories/add/", views.admin_add_subcategory, name="admin_add_subcategory"),
    path("admin/subcategories/<int:pk>/edit/", views.admin_edit_subcategory, name="admin_edit_subcategory"),
    path("admin/subcategories/<int:pk>/delete/", views.admin_delete_subcategory, name="admin_delete_subcategory"),

    path("admin/sections/", views.admin_sections, name="admin_sections"),
    path("admin/sections/add/", views.admin_add_section, name="admin_add_section"),
    path("admin/sections/<int:pk>/edit/", views.admin_edit_section, name="admin_edit_section"),
    path("admin/sections/<int:pk>/delete/", views.admin_delete_section, name="admin_delete_section"),

    path("admin/reviews/", views.admin_reviews, name="admin_reviews"),
    path("admin/reviews/<int:pk>/approve/", views.admin_approve_review, name="admin_approve_review"),
    path("admin/reviews/<int:pk>/delete/", views.admin_delete_review, name="admin_delete_review"),
]

