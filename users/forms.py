from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email не найден"
            )
        return email


class RegisterForm(UserCreationForm):
    # ❌ убираем лишние поля
    email = forms.EmailField(required=True)
    # phone = forms.CharField(required=False, max_length=30)
    # address = forms.CharField(
    #     required=False,
    #     max_length=255,
    #     widget=forms.TextInput(attrs={"placeholder": "Адрес доставки"}),
    # )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            # "phone",
            # "address",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class", "w-full p-2 rounded border"
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        # ❌ больше не используем
        # user.phone = self.cleaned_data.get("phone")
        # user.address = self.cleaned_data.get("address")

        if commit:
            user.save()
        return user