from rest_framework import serializers
from .models import Route
from users.models import User  

class RouteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Связь с моделью User

    class Meta:
        model = Route
        fields = ['id', 'name', 'user', 'coords', 'distance']


