from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user. We add phone number and country because
    most users will be in Uganda (MTN/Airtel numbers).
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=2, default='UG')
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or self.email
