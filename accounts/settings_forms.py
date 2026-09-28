import zoneinfo

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from .data.countries import COUNTRIES


User = get_user_model()


def get_timezone_choices():
    """
    Return a list of (tz_name, friendly_label) sorted by region, then name.

    Example output:
        [('Africa/Abidjan', 'Africa / Abidjan'),
         ('Africa/Kampala', 'Africa / Kampala'),
         ('America/New_York', 'America / New York'),
         ...]
    """
    tz_names = sorted(zoneinfo.available_timezones())
    choices = []
    for tz in tz_names:
        # Skip odd internal zones like 'Factory' if any exist
        if tz in ('Factory', 'localtime'):
            continue
        friendly = tz.replace('_', ' ').replace('/', ' / ')
        choices.append((tz, friendly))
    return choices


class ProfileForm(forms.ModelForm):
    """Edit your name, contact details, avatar, and country."""

    COUNTRY_CHOICES = [(code, f"{name} ({dial})") for code, name, dial in COUNTRIES]

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
        })
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'phone_number', 'country', 'avatar',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100',
                'accept': 'image/*',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('That email is already used by another account.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be under 5 MB.')
        return avatar


class NotificationPreferencesForm(forms.ModelForm):
    """Toggle email notifications by category."""

    class Meta:
        model = User
        fields = (
            'notify_email_security',
            'notify_email_family',
            'notify_email_app_requests',
            'notify_email_billing',
        )


class PrivacyPreferencesForm(forms.ModelForm):
    """Choose how long location history is kept."""

    class Meta:
        model = User
        fields = ('location_retention_days',)
        widgets = {
            'location_retention_days': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
            }),
        }


class PreferencesForm(forms.ModelForm):
    """Language, dark mode, timezone."""

    timezone = forms.ChoiceField(
        choices=[],  # filled in __init__
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
        }),
    )

    class Meta:
        model = User
        fields = ('language', 'dark_mode', 'timezone')
        widgets = {
            'language': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
            }),
            'dark_mode': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = get_timezone_choices()

        # Ensure the user's current timezone is in the choices list.
        # If somehow it isn't (e.g. saved value from an older format),
        # add it as the first option so the form still renders.
        current = None
        if self.instance and self.instance.pk:
            current = self.instance.timezone
        if current and current not in dict(choices):
            choices = [(current, current.replace('_', ' '))] + choices

        self.fields['timezone'].choices = choices

        # Provide a sensible default if this is a new user.
        if not current:
            self.fields['timezone'].initial = 'Africa/Kampala'


class StyledPasswordChangeForm(PasswordChangeForm):
    """Django's PasswordChangeForm with Tailwind classes on the widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            })
