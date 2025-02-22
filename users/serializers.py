# users/serializers.py

from rest_framework import serializers
from .models import User

class FireBaseAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firebase_user_id', 'avatar']
        read_only_fields = ['id', 'firebase_user_id']

class UploadAvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField()
