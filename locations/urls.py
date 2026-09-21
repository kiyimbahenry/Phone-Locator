from django.urls import path
from .views import LocationPingView, LatestLocationsView, EventCreateView

urlpatterns = [
    path('ping/', LocationPingView.as_view(), name='location-ping'),
    path('latest/', LatestLocationsView.as_view(), name='location-latest'),
    path('events/', EventCreateView.as_view(), name='event-create'),
]
