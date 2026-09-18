from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


# IMEI is 15 digits. We validate the shape only; real IMEI validation
# requires the Luhn checksum, which we can add later.
imei_validator = RegexValidator(
    regex=r'^\d{15}$',
    message='IMEI must be exactly 15 digits.'
)

# Serial numbers vary wildly by manufacturer. We just enforce a safe charset.
serial_validator = RegexValidator(
    regex=r'^[A-Za-z0-9\-]{4,32}$',
    message='Serial number must be 4–32 characters (letters, digits, hyphens).'
)


class Device(models.Model):
    """
    A phone that a user has registered with Phone-Locator.

    The IMEI / serial / phone number are stored for IDENTIFICATION and
    for reporting to carriers or police. They do NOT give us a GPS
    location — only the app on the device itself can do that.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        LOST = 'lost', 'Lost'
        STOLEN = 'stolen', 'Stolen'
        RECOVERED = 'recovered', 'Recovered'
        RETIRED = 'retired', 'Retired'

    class Platform(models.TextChoices):
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'iOS'
        OTHER = 'other', 'Other'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices',
    )

    # --- Identifiers (all optional except nickname) ---
    nickname = models.CharField(
        max_length=60,
        help_text="Friendly name, e.g. 'Sarah's Samsung A55'"
    )
    platform = models.CharField(
        max_length=10,
        choices=Platform.choices,
        default=Platform.ANDROID,
    )
    imei = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[imei_validator],
        help_text='15-digit IMEI. Optional but recommended.',
    )
    serial_number = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        validators=[serial_validator],
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    account_email = models.EmailField(
        null=True,
        blank=True,
        help_text='Google/Apple account email used on the device (for ID only).',
    )

    # --- Status & consent ---
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    consent_given = models.BooleanField(
        default=False,
        help_text='Owner has agreed that this app may collect location for this device.',
    )
    consent_given_at = models.DateTimeField(null=True, blank=True)

    # --- Timestamps ---
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when the device app checks in.',
    )

    class Meta:
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['imei']),
        ]

    def __str__(self):
        return f'{self.nickname} ({self.get_status_display()})'

    @property
    def is_lost_or_stolen(self):
        return self.status in (self.Status.LOST, self.Status.STOLEN)
