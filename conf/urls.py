from django.contrib import admin
from django.urls import path, include
from route.views import showroute
from healthcheck import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', healthCheck.as_view()),
    path('api/users/', include('users.urls')),
    path('route/<str:lat1>,<str:long1>,<str:lat2>,<str:long2>', showroute, name='showroute'),
]
