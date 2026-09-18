from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'nickname', 'owner', 'platform', 'status',
        'imei', 'phone_number', 'last_seen_at',
    )
    list_filter = ('status', 'platform', 'consent_given')
    search_fields = ('nickname', 'imei', 'serial_number', 'phone_number', 'owner__username')
    readonly_fields = ('registered_at', 'updated_at', 'last_seen_at', 'consent_given_at')
    raw_id_fields = ('owner',)
