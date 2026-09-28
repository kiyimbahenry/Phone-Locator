from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user. We add phone number, country, avatar, and
    notification preferences because Phone-Locator needs them.
    """

    class Language(models.TextChoices):
        # African
        ENGLISH = 'en', 'English'
        LUGANDA = 'lg', 'Luganda'
        SWAHILI = 'sw', 'Swahili'
        FRENCH = 'fr', 'Français (French)'
        ARABIC = 'ar', 'العربية (Arabic)'
        PORTUGUESE = 'pt', 'Português (Portuguese)'

        # European
        SPANISH = 'es', 'Español (Spanish)'
        GERMAN = 'de', 'Deutsch (German)'
        ITALIAN = 'it', 'Italiano (Italian)'
        DUTCH = 'nl', 'Nederlands (Dutch)'
        RUSSIAN = 'ru', 'Русский (Russian)'
        LATIN = 'la', 'Latina (Latin)'

        # Asian
        CHINESE_SIMPLIFIED = 'zh-hans', '中文（简体）(Chinese Simplified)'
        CHINESE_TRADITIONAL = 'zh-hant', '中文（繁體）(Chinese Traditional)'
        JAPANESE = 'ja', '日本語 (Japanese)'
        KOREAN = 'ko', '한국어 (Korean)'
        HINDI = 'hi', 'हिन्दी (Hindi)'

    # --- Identity ---
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=2, default='UG')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True, null=True,
        help_text='Profile picture shown in the navbar.',
    )
    is_phone_verified = models.BooleanField(default=False)

    # --- Privacy & data ---
    class Retention(models.IntegerChoices):
        DAYS_7 = 7, '7 days'
        DAYS_30 = 30, '30 days'
        DAYS_90 = 90, '90 days'
        FOREVER = 0, 'Keep forever'

    location_retention_days = models.IntegerField(
        choices=Retention.choices,
        default=Retention.DAYS_90,
        help_text='How long location history is kept before automatic deletion.',
    )

    # --- Email notification preferences ---
    notify_email_security = models.BooleanField(
        default=True,
        help_text='SIM changes, failed unlocks, stolen-device alerts.',
    )
    notify_email_family = models.BooleanField(
        default=True,
        help_text='Arrivals, departures, screen-time events for your children.',
    )
    notify_email_app_requests = models.BooleanField(
        default=True,
        help_text='When a child requests approval for an app.',
    )
    notify_email_billing = models.BooleanField(
        default=True,
        help_text='Subscription renewals, receipts, payment issues.',
    )

    # --- Preferences ---
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.ENGLISH,
    )
    dark_mode = models.BooleanField(default=False)
    timezone = models.CharField(max_length=64, default='Africa/Kampala')

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or self.email

    @property
    def display_name(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return full or self.username

    @property
    def initials(self):
        first = (self.first_name or self.username or '?')[:1]
        last = (self.last_name or '')[:1]
        return (first + last).upper()
