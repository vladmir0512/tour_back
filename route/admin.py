from django.contrib import admin
from .models import Route
# Register your models here.
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    fields = ["name",  "user", "distance", "rating", "comment", "coords", "created_at"]
