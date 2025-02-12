from django.urls import path
from . import views

urlpatterns = [
    # crud 
    # 
    # for ROUTES
    path('routes/', views.ApiRouteOverview, name='routes'),
    path('routes/create/', views.add_route, name='add-route'),
    path('routes/list/', views.view_routes, name='view_routes'),
    path('routes/update/<int:pk>/', views.update_route, name='update-route'),
    path('routes/delete/<int:pk>/', views.delete_route, name='delete-comment'),

    # for COMMENTS
    path('comments/', views.ApiCommentOverview, name='comments'),
    path('comments/create/', views.add_comment, name='add-comment'),
    path('comments/list/', views.view_comments, name='view_comments'),
    path('comments/update/<int:pk>/', views.update_comment, name='update-comment'),
    path('comments/delete/<int:pk>/', views.delete_comment, name='delete-comment'),

    # for USERS
    path('users/', views.ApiUserOverview, name='users'),
    path('users/create/', views.add_user, name='add-user'),
    path('users/list/', views.view_users, name='view_user'),
    path('users/update/<int:pk>/', views.update_user, name='update-user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete-user'),

]