from django.contrib import admin
from .models import User
# Register your models here.
@admin.register(User)
class User(admin.ModelAdmin):
    fields = ["username", "firebase_user_id", "email", "avatar"]
