from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/locations/', include('locations.urls')),
    path('parenting/', include('parenting.urls')),
    path('', include('dashboard.urls')),
]

# Serve uploaded media files (avatars) during development only.
# In production, a real web server or CDN should serve these.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
