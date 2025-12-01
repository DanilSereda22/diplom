# apps/orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "delivery_method",
            "comment",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "comment": forms.Textarea(attrs={"rows": 3}),
            "delivery_method": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delivery_method"].choices = [
            ("courier", "Курьер"),
            ("pickup", "Самовывоз"),
        ]
        self.fields["first_name"].widget.attrs["placeholder"] = "Имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Фамилия"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["phone"].widget.attrs["placeholder"] = "Телефон"
        self.fields["address"].widget.attrs["placeholder"] = "Адрес (если выбран курьер)"
        for name, field in self.fields.items():
            if name != "delivery_method":
                field.widget.attrs.update({
                    "class": (
                        "w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 "
                        "focus:bg-white focus:border-pink-300 focus:ring-4 "
                        "focus:ring-pink-100 outline-none transition-all"
                    )
                })
