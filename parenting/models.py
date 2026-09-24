import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_pairing_code():
    """6-digit numeric code, e.g. 847219."""
    return f"{secrets.randbelow(1000000):06d}"


class Child(models.Model):
    """
    A child monitored by a parent through Phone-Locator.

    A child is linked to a Device (already registered via the Devices page).
    One parent can have many children.
    """

    class AgeGroup(models.TextChoices):
        UNDER_13 = 'under_13', 'Under 13'
        TEEN = 'teen', 'Teen (13–17)'

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children',
    )
    device = models.OneToOneField(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='child_profile',
        help_text="The child's phone, already registered as a Device.",
    )
    name = models.CharField(max_length=60)
    age_group = models.CharField(
        max_length=10,
        choices=AgeGroup.choices,
        default=AgeGroup.TEEN,
    )

    # Uganda DPPA requires documented parental consent
    parental_consent_given = models.BooleanField(
        default=False,
        help_text='Parent/guardian has confirmed they are authorised to monitor this child.',
    )
    parental_consent_at = models.DateTimeField(null=True, blank=True)

    # Has the child app linked using a pairing code?
    is_paired = models.BooleanField(
        default=False,
        help_text='True once the child app has been linked with the pairing code.',
    )
    paired_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.parent.username})'


class PairingCode(models.Model):
    """Short-lived code used to link the child app to this Child record."""

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='pairing_codes',
    )
    code = models.CharField(max_length=6, default=generate_pairing_code)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at

    def __str__(self):
        return f'{self.code} for {self.child.name}'


class AppRule(models.Model):
    """A parent's rule for a specific app on the child's phone."""

    class Status(models.TextChoices):
        ALLOWED = 'allowed', 'Allowed'
        LIMITED = 'limited', 'Limited'
        BLOCKED = 'blocked', 'Blocked'

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='app_rules',
    )
    app_identifier = models.CharField(
        max_length=200,
        help_text="Android package name or iOS bundle id, e.g. com.zhiliaoapp.musically",
    )
    app_name = models.CharField(max_length=100)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ALLOWED,
    )
    daily_limit_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Only used when status=LIMITED.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('child', 'app_identifier')
        ordering = ['app_name']

    def __str__(self):
        return f'{self.app_name} — {self.get_status_display()}'


class ScreenTimeRule(models.Model):
    """Daily screen-time limits and bedtime for a child."""

    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name='screen_time_rule',
    )
    weekday_limit_minutes = models.PositiveIntegerField(
        default=120,
        help_text='Total daily limit, Monday–Friday.',
    )
    weekend_limit_minutes = models.PositiveIntegerField(
        default=240,
        help_text='Total daily limit, Saturday–Sunday.',
    )
    bedtime_start = models.TimeField(
        null=True, blank=True,
        help_text='e.g. 21:00 — device locks at this time.',
    )
    bedtime_end = models.TimeField(
        null=True, blank=True,
        help_text='e.g. 07:00 — device unlocks at this time.',
    )
    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Screen time for {self.child.name}'


class WebFilterLog(models.Model):
    """One row per blocked website attempt reported by the child's VPN."""

    class Category(models.TextChoices):
        ADULT = 'adult', 'Adult content'
        GAMBLING = 'gambling', 'Gambling'
        VIOLENCE = 'violence', 'Violence'
        DANGEROUS = 'dangerous', 'Dangerous content'
        CUSTOM = 'custom', 'Custom block'

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='web_filter_logs',
    )
    domain = models.CharField(max_length=255)
    category = models.CharField(max_length=12, choices=Category.choices)
    blocked_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['child', '-blocked_at']),
        ]

    def __str__(self):
        return f'{self.domain} ({self.get_category_display()})'


class AppUsageLog(models.Model):
    """Daily aggregated app usage reported by the child's phone."""

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='app_usage_logs',
    )
    app_identifier = models.CharField(max_length=200)
    app_name = models.CharField(max_length=100)

    day = models.DateField()
    total_minutes = models.PositiveIntegerField(default=0)

    first_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('child', 'app_identifier', 'day')
        ordering = ['-day', '-total_minutes']
        indexes = [
            models.Index(fields=['child', '-day']),
        ]

    def __str__(self):
        return f'{self.app_name} — {self.day} ({self.total_minutes}m)'


class ParentingAlert(models.Model):
    """A notification for the parent about one of their children."""

    class Kind(models.TextChoices):
        APP_INSTALLED = 'app_installed', 'App installed'
        APP_BLOCKED = 'app_blocked', 'App blocked'
        WEB_BLOCKED = 'web_blocked', 'Website blocked'
        LIMIT_REACHED = 'limit_reached', 'Screen time limit reached'
        BEDTIME_START = 'bedtime_start', 'Bedtime started'
        LOW_BATTERY = 'low_battery', 'Low battery'
        ARRIVED_SCHOOL = 'arrived_school', 'Arrived at school'
        LEFT_SCHOOL = 'left_school', 'Left school'
        PAIRED = 'paired', 'Device paired'
        UNPAIRED = 'unpaired', 'Device unpaired'

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='alerts',
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    message = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    occurred_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['child', '-occurred_at']),
            models.Index(fields=['child', 'is_read']),
        ]

    def __str__(self):
        return f'{self.child.name} — {self.get_kind_display()}'
