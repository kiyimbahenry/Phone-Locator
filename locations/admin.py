from django.contrib import admin
from .models import Location, DeviceEvent


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'device', 'latitude', 'longitude',
        'accuracy_m', 'source', 'battery_percent',
        'recorded_at', 'received_at',
    )
    list_filter = ('source', 'network_operator')
    search_fields = ('device__nickname', 'device__imei')
    raw_id_fields = ('device',)
    date_hierarchy = 'recorded_at'
    readonly_fields = ('received_at',)


@admin.register(DeviceEvent)
class DeviceEventAdmin(admin.ModelAdmin):
    list_display = (
        'device', 'kind', 'occurred_at', 'is_read',
        'latitude', 'longitude', 'battery_percent',
    )
    list_filter = ('kind', 'is_read')
    search_fields = ('device__nickname', 'device__imei', 'message')
    raw_id_fields = ('device',)
    date_hierarchy = 'occurred_at'
    readonly_fields = ('received_at',)
