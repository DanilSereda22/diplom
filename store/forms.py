# apps/store/forms.py
from django import forms
from .models import Product, Category, SubCategory, HomeSection

class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Поиск по товарам...",
            "class": "w-full p-2 rounded border",
        })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "slug", "category", "description",
            "price", "stock", "weight", "image", "available"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Ставим класс для всех полей
            field.widget.attrs.update({"class": "w-full p-2 rounded border"})
            # Делам slug readonly
            if field_name == "slug":
                field.widget.attrs.update({"readonly": "readonly"})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "w-full p-2 rounded border"})
            if field_name == "slug":
                field.widget.attrs.update({"readonly": "readonly"})


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ["category", "name", "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "w-full p-2 rounded border"})
            if field_name == "slug":
                field.widget.attrs.update({"readonly": "readonly"})


class HomeSectionForm(forms.ModelForm):
    class Meta:
        model = HomeSection
        fields = ["title", "slug", "products", "is_active", "order"]
        widgets = {
            "products": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "products":
                field.widget.attrs.update({"class": "w-full p-2 rounded border"})
            if field_name == "slug":
                field.widget.attrs.update({"readonly": "readonly"})
