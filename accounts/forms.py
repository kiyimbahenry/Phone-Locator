from django import forms
from django.contrib.auth import get_user_model

from .data.countries import COUNTRIES


User = get_user_model()


class DashboardRegisterForm(forms.Form):
    """
    Registration form used by the dashboard's Create Account modal.
    Uses first_name / last_name + email as the primary identifiers.
    """

    COUNTRY_CHOICES = [(code, f"{name} ({dial})") for code, name, dial in COUNTRIES]

    first_name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': '+256 700 000 000',
            'autocomplete': 'tel',
        })
    )
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        initial='UG',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
        })
    )
    password1 = forms.CharField(
        label='Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'At least 8 characters',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'Repeat password',
            'autocomplete': 'new-password',
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with that email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        # Derive a username from the email prefix; ensure uniqueness.
        base = data['email'].split('@')[0][:20] or 'user'
        username = base
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            counter += 1
            username = f'{base}{counter}'

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            country=data['country'],
        )
        return user
