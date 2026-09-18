from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/locations/', include('locations.urls')),
    path('api/locations/', include('locations.urls')),
]
