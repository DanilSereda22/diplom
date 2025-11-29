# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField("Телефон", max_length=30, blank=True)
    address = models.TextField("Адрес", blank=True)

    def __str__(self):
        return self.get_full_name() or self.username
