# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField("Телефон", max_length=30, blank=True)
    address = models.CharField("Адрес доставки", max_length=255, blank=True)
    bonus_points = models.DecimalField("Бонусы", max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.get_full_name() or self.username
