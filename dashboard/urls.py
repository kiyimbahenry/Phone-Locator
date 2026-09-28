from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),

    # Registration (server-rendered, from the login page)
    path('register/', views.register_view, name='register'),

    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/',
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/',
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # Other dashboard pages
    path('devices/', views.devices_view, name='devices'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/status/', views.device_status, name='device_status'),
    path('locations/', views.locations_view, name='locations'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/profile/', views.settings_profile, name='settings_profile'),
    path('settings/notifications/', views.settings_notifications, name='settings_notifications'),
    path('settings/privacy/', views.settings_privacy, name='settings_privacy'),
    path('settings/preferences/', views.settings_preferences, name='settings_preferences'),
    path('settings/password/', views.settings_password, name='settings_password'),
    path('settings/security/', views.settings_security, name='settings_security'),
    path('settings/download-data/', views.settings_download_data, name='settings_download_data'),
    path('settings/delete-account/', views.settings_delete_account, name='settings_delete_account'),
]
