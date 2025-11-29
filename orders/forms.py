# apps/orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "phone", "address", "delivery_method", "comment"]
        widgets = {
            "address": forms.Textarea(attrs={"rows":3}),
            "comment": forms.Textarea(attrs={"rows":3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "w-full p-2 rounded border")
