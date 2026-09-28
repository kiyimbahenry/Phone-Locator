from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'phone_number', 'country',
        'is_phone_verified', 'is_staff', 'created_at',
    )
    list_filter = (
        'country', 'is_phone_verified', 'is_staff',
        'notify_email_security', 'notify_email_family',
    )
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    fieldsets = UserAdmin.fieldsets + (
        ('Phone-Locator', {
            'fields': ('phone_number', 'country', 'avatar', 'is_phone_verified'),
        }),
        ('Privacy & Data', {
            'fields': ('location_retention_days',),
        }),
        ('Email Notifications', {
            'fields': (
                'notify_email_security',
                'notify_email_family',
                'notify_email_app_requests',
                'notify_email_billing',
            ),
        }),
        ('Preferences', {
            'fields': ('language', 'dark_mode', 'timezone'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
