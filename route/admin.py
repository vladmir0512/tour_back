from django.contrib import admin
from .models import Comment, Route
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ["route", "text", "user","created_at"]

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    fields = ["name",  "user", "distance", "coords", "created_at",]
