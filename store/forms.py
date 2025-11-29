# apps/store/forms.py
from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        "placeholder": "Поиск по товарам...",
        "class": "w-full p-2 rounded border",
    }))
