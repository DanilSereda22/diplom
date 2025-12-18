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
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Самовывоз по умолчанию
        self.instance.delivery_method = "pickup"

        self.fields["first_name"].widget.attrs["placeholder"] = "Имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Фамилия"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["phone"].widget.attrs["placeholder"] = "Телефон"

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": (
                    "w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 "
                    "focus:bg-white focus:border-pink-300 focus:ring-4 "
                    "focus:ring-pink-100 outline-none transition-all"
                )
            })
