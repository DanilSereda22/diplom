from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=30)
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tailwind классы
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full p-2 rounded border")

    def save(self, commit=True):
        user = super().save(commit=False)

        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")

        if commit:
            user.save()

        return user
