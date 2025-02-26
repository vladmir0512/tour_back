from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    #-------------------------------------------------CRUD--------------------------------------------------
    # for ROUTES
    path('routes/', views.ApiRouteOverview, name='routes'),
    path('routes/create/', views.add_route, name='add-route'),
    path('routes/list/', views.view_routes, name='view_routes'),
    path('routes/update/<int:pk>/', views.update_route, name='update-route'),
    path('routes/delete/<int:pk>/', views.delete_route, name='delete-comment'),

  
    # for USERS
    path('users/', views.ApiUserOverview, name='users'),
    path('users/create/', views.add_user, name='add-user'),
    path('users/list/', views.view_users, name='view_user'),
    path('users/update/<int:pk>/', views.update_user, name='update-user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete-user'),
    #-------------------------------------------------------------------------------------------------------
    
    #-------------------------------------------------SEARCH COORDS(address to coords)--------------------------------------------------
    path('search/', views.search_address, name='search_address'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
