from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    """
    Dashboard form to register a new device.

    We only ask for the essentials:
      - a friendly nickname
      - the phone number / email on the phone (for identification)
      - IMEI and serial (optional, but useful for reporting to police)
      - consent

    The mobile app will fill in manufacturer / model / platform
    automatically once it's installed on the device.
    """

    class Meta:
        model = Device
        fields = [
            'nickname',
            'phone_number',
            'account_email',
            'imei',
            'serial_number',
            'consent_given',
        ]
        widgets = {
            'nickname': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "e.g. Mum's phone",
            }),
            'os_version': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "iOS 17.4 / Android 13",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "+256 700 000 000",
            }),
            'account_email': forms.EmailInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "email on the phone (optional)",
            }),
            'imei': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "15 digits (optional but recommended)",
                'maxlength': '15',
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': "optional",
            }),
            'consent_given': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500',
            }),
        }

    def clean_imei(self):
        imei = self.cleaned_data.get('imei')
        if not imei:
            return imei
        if not imei.isdigit():
            raise forms.ValidationError("IMEI must contain digits only.")
        if len(imei) != 15:
            raise forms.ValidationError("IMEI must be exactly 15 digits.")
        return imei

    def clean_consent_given(self):
        consent = self.cleaned_data.get('consent_given')
        if not consent:
            raise forms.ValidationError(
                "You must agree to location collection before registering a device."
            )
        return consent
