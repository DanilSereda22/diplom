from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

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
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full p-2 rounded border")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        if commit:
            user.save()
        return user
