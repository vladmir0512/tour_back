# users/urls.py

from django.urls import path
from .views import RegisterView, LoginView, UploadAvatarView, GetUserAvatarView, get_routes, get_routes_users, update_rating, add_comment

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload-avatar/', UploadAvatarView.as_view(), name='upload_avatar'),
    path('avatar/', GetUserAvatarView.as_view(), name='get_user_avatar'),
    path('routes/', get_routes, name='get_routes'),
    path('routes/update-rating/', update_rating, name='update_rating'),
    path('routes/add-comment/', add_comment, name='add_comment'),
    path('<str:uid>/routes/', get_routes_users, name='get_routes_users'),
    path('routes/', get_routes, name='get_routes')
]
