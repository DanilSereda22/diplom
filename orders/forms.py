from django import forms
from .models import Order

BASE_INPUT = "w-full p-3 rounded-xl border border-gray-200 bg-gray-50"

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
            "delivery_method",
            "delivery_address",
            "delivery_comment",
        )

        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "phone": "Телефон",
            "email": "Электронная почта",
            "delivery_method": "Способ получения",
            "delivery_address": "Адрес доставки",
            "delivery_comment": "Комментарий к доставке",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"class": BASE_INPUT, "placeholder": "Имя"}),
            "last_name": forms.TextInput(attrs={"class": BASE_INPUT, "placeholder": "Фамилия"}),
            "phone": forms.TextInput(attrs={
                "class": BASE_INPUT,
                "placeholder": "+7 (___) ___-__-__",
                "id": "phone"
            }),
            "email": forms.EmailInput(attrs={"class": BASE_INPUT}),
            "delivery_method": forms.Select(attrs={"class": BASE_INPUT}),
            "delivery_address": forms.TextInput(attrs={"class": BASE_INPUT}),
            "delivery_comment": forms.Textarea(attrs={
                "class": BASE_INPUT,
                "rows": 2
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delivery_method"].choices = Order.DELIVERY_CHOICES

    def clean(self):
        if self.cleaned_data.get("delivery_method") == "delivery" \
           and not self.cleaned_data.get("delivery_address"):
            self.add_error("delivery_address", "Укажите адрес доставки")
        return self.cleaned_data
    


