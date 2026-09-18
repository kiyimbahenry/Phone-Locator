from django.urls import path
from .views import LocationPingView, LatestLocationsView

urlpatterns = [
    path('ping/', LocationPingView.as_view(), name='location-ping'),
    path('latest/', LatestLocationsView.as_view(), name='location-latest'),
]
