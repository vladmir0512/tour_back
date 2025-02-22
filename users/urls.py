# users/urls.py

from django.urls import path
from .views import RegisterView, LoginView, UploadAvatarView, GetUserAvatarView  # Добавляем новый импорт

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload-avatar/', UploadAvatarView.as_view(), name='upload_avatar'),  # Новый маршрут для загрузки изображения
    path('avatar/', GetUserAvatarView.as_view(), name='get_user_avatar')
]
