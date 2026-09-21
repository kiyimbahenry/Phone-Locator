from django.db import models


class Location(models.Model):
    """
    A single GPS/network ping from a registered device.

    We store accuracy so the map can show a circle of uncertainty
    rather than a fake precise pin.
    """

    class Source(models.TextChoices):
        GPS = 'gps', 'GPS'
        NETWORK = 'network', 'Wi-Fi / Network'
        CELL = 'cell', 'Cell tower'
        LAST_KNOWN = 'last_known', 'Last known'

    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='locations',
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_m = models.FloatField(
        null=True, blank=True,
        help_text='Estimated accuracy radius in metres.'
    )
    altitude_m = models.FloatField(null=True, blank=True)
    speed_mps = models.FloatField(null=True, blank=True)
    heading_deg = models.FloatField(null=True, blank=True)

    source = models.CharField(
        max_length=16,
        choices=Source.choices,
        default=Source.GPS,
    )

    battery_percent = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='0–100, if the device reported it.'
    )
    network_operator = models.CharField(
        max_length=40, null=True, blank=True,
        help_text="e.g. 'MTN', 'Airtel'."
    )

    # This is the time the DEVICE says it recorded the fix.
    recorded_at = models.DateTimeField()
    # This is the time the SERVER stored the row.
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['device', '-recorded_at']),
        ]

    def __str__(self):
        return f'{self.device.nickname} @ {self.recorded_at:%Y-%m-%d %H:%M}'

class DeviceEvent(models.Model):
    """
    A security-relevant event reported by the device app.

    Everything here is an *event log*, not surveillance — the app
    never reads messages, contacts, or files. It only reports things
    the OS itself allows any app to observe.

    These events are shown on the dashboard and can trigger alerts.
    """

    class Kind(models.TextChoices):
        # Device state
        POWER_OFF = 'power_off', 'Power off requested'
        POWER_ON = 'power_on', 'Device powered on'
        LOW_BATTERY = 'low_battery', 'Battery low'
        AIRPLANE_MODE_ON = 'airplane_mode_on', 'Airplane mode enabled'
        LOCATION_OFF = 'location_off', 'Location services turned off'

        # SIM
        SIM_REMOVED = 'sim_removed', 'SIM card removed'
        SIM_INSERTED = 'sim_inserted', 'SIM card inserted'
        SIM_CHANGED = 'sim_changed', 'SIM card changed'

        # Unlock
        FAILED_UNLOCK = 'failed_unlock', 'Failed unlock attempt'
        TOO_MANY_FAILED_UNLOCKS = 'too_many_failed_unlocks', 'Too many failed unlock attempts'

        # Recovery
        MARKED_LOST = 'marked_lost', 'Marked as lost'
        MARKED_STOLEN = 'marked_stolen', 'Marked as stolen'
        RECOVERED = 'recovered', 'Marked as recovered'

    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='events',
    )

    kind = models.CharField(max_length=32, choices=Kind.choices)
    message = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(
        null=True, blank=True,
        help_text="Extra details, e.g. {'old_sim': '...', 'new_sim': '...'}"
    )

    # Snapshot of location at the time of the event (if known)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    battery_percent = models.PositiveSmallIntegerField(null=True, blank=True)

    occurred_at = models.DateTimeField(
        help_text='When the device says the event happened.'
    )
    received_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['device', '-occurred_at']),
            models.Index(fields=['device', 'is_read']),
        ]

    def __str__(self):
        return f'{self.device.nickname} — {self.get_kind_display()}'
