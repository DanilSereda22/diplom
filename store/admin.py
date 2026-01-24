# store/admin.py
from django.contrib import admin
from .models import Category, SubCategory, Product,HomeSection,ShopReview

@admin.register(ShopReview)
class ShopReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"
    
@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("products",)

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price","stock", "available", "created")
    list_filter = ("available", "category")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
