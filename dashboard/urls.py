from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),

    path('devices/', views.devices_view, name='devices'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/status/', views.device_status, name='device_status'),

    path('locations/', views.locations_view, name='locations'),
    path('family/', views.family_view, name='family'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('settings/', views.settings_view, name='settings'),
]
