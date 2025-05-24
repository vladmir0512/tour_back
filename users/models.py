# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    firebase_user_id = models.CharField(max_length=28, null=True, blank=True)

    def __str__(self: "CustomUser") -> str:
        return f"{self.email}"

class User(models.Model):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    email = models.EmailField(null=True, blank=True)
    firebase_user_id = models.CharField(max_length=28, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  

    def __str__(self: "User") -> str:
        return f"{self.email}"