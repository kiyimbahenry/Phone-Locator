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
