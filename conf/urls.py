from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from route.views import showroute
from healthcheck import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', healthCheck.as_view()),
    path('api/users/', include('users.urls')),
    path('api/', include('api.urls')),

    # path('route/фвв', showroute, name='showroute'),

    path('route/<str:lat1>,<str:long1>,<str:lat2>,<str:long2>', showroute, name='showroute'),
]
# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)