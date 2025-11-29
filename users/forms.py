from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=30)
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tailwind классы
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full p-2 rounded border")

    def save(self, commit=True):
        user = super().save(commit=True)

        # создаём профиль
        CustomUser.objects.create(
            user=user,
            phone=self.cleaned_data.get("phone"),
            address=self.cleaned_data.get("address"),
        )
        return user
