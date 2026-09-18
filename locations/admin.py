from django.contrib import admin
from .models import Location


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
