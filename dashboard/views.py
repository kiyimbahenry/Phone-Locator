from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from devices.forms import DeviceForm
from devices.models import Device
from locations.models import DeviceEvent
from accounts.forms import DashboardRegisterForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from accounts.settings_forms import (
    ProfileForm,
    NotificationPreferencesForm,
    PrivacyPreferencesForm,
    PreferencesForm,
    StyledPasswordChangeForm,
)
from accounts.models import User


class DashboardLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['register_form'] = DashboardRegisterForm()
        return ctx


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard:login')


def register_view(request):
    """Handles the create-account form posted from the login page modal."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = DashboardRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Welcome, {user.username}! Your account is ready. Please log in."
            )
            return redirect('dashboard:login')
        else:
            messages.error(request, "Please fix the errors below and try again.")
            return render(request, 'registration/login.html', {
                'form': LoginView().get_form_class()(request),
                'register_form': form,
                'show_register_modal': True,
            })

    return redirect('dashboard:login')


@login_required
def home(request):
    devices = Device.objects.filter(owner=request.user)
    unread_alerts = DeviceEvent.objects.filter(
        device__owner=request.user, is_read=False
    ).count()

    return render(request, 'dashboard/home.html', {
        'devices': devices,
        'device_count': devices.count(),
        'active_count': devices.filter(status=Device.Status.ACTIVE).count(),
        'lost_count': devices.filter(
            status__in=[Device.Status.LOST, Device.Status.STOLEN]
        ).count(),
        'family_count': 0,
        'unread_alerts': unread_alerts,
    })


@login_required
def devices_view(request):
    devices = Device.objects.filter(owner=request.user)

    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.owner = request.user
            if device.consent_given and not device.consent_given_at:
                device.consent_given_at = timezone.now()
            device.save()
            messages.success(request, f"Device '{device.nickname}' registered.")
            return redirect('dashboard:devices')
    else:
        form = DeviceForm()

    return render(request, 'dashboard/devices.html', {
        'devices': devices,
        'form': form,
    })


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk, owner=request.user)
    latest = device.locations.order_by('-recorded_at').first()
    events = device.events.order_by('-occurred_at')[:50]

    return render(request, 'dashboard/device_detail.html', {
        'device': device,
        'latest': latest,
        'events': events,
    })


@login_required
def device_status(request, pk):
    if request.method != 'POST':
        return redirect('dashboard:device_detail', pk=pk)

    device = get_object_or_404(Device, pk=pk, owner=request.user)
    new_status = request.POST.get('status')

    valid = {c[0] for c in Device.Status.choices}
    if new_status in valid:
        device.status = new_status
        device.save(update_fields=['status', 'updated_at'])
        messages.success(
            request,
            f"'{device.nickname}' marked as {device.get_status_display()}."
        )

    return redirect('dashboard:device_detail', pk=pk)


@login_required
def locations_view(request):
    device_qs = Device.objects.filter(owner=request.user).order_by('-last_seen_at')
    rows = []
    for device in device_qs:
        latest = device.locations.order_by('-recorded_at').first()
        rows.append({'device': device, 'location': latest})

    return render(request, 'dashboard/locations.html', {'devices': rows})


@login_required
def alerts_view(request):
    base_qs = DeviceEvent.objects.filter(device__owner=request.user)
    unread_count = base_qs.filter(is_read=False).count()
    events = base_qs.order_by('-occurred_at')[:100]

    return render(request, 'dashboard/alerts.html', {
        'events': events,
        'unread_count': unread_count,
    })


@login_required
def subscription_view(request):
    return render(request, 'dashboard/subscription.html')


@login_required
def settings_view(request):
    """Overview page: links to Profile, Notifications, Privacy, Security."""
    return render(request, 'dashboard/settings.html')


@login_required
def settings_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('dashboard:settings_profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'dashboard/settings_profile.html', {'form': form})


@login_required
def settings_notifications(request):
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences saved.')
            return redirect('dashboard:settings_notifications')
    else:
        form = NotificationPreferencesForm(instance=request.user)

    return render(request, 'dashboard/settings_notifications.html', {'form': form})


@login_required
def settings_privacy(request):
    if request.method == 'POST':
        form = PrivacyPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings saved.')
            return redirect('dashboard:settings_privacy')
    else:
        form = PrivacyPreferencesForm(instance=request.user)

    return render(request, 'dashboard/settings_privacy.html', {'form': form})


@login_required
def settings_preferences(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences saved.')
            return redirect('dashboard:settings_preferences')
    else:
        form = PreferencesForm(instance=request.user)

    return render(request, 'dashboard/settings_preferences.html', {'form': form})


@login_required
def settings_password(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard:settings_password')
    else:
        form = StyledPasswordChangeForm(user=request.user)

    return render(request, 'dashboard/settings_password.html', {'form': form})


@login_required
def settings_security(request):
    """Placeholder — we'll wire real session tracking later."""
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    # Recent device events across all the user's devices
    recent_events = DeviceEvent.objects.filter(
        device__owner=request.user
    ).order_by('-occurred_at')[:20]

    return render(request, 'dashboard/settings_security.html', {
        'recent_events': recent_events,
        'current_session_key': request.session.session_key,
    })


@login_required
def settings_download_data(request):
    """Return a JSON dump of everything we hold about this user."""
    from django.http import JsonResponse

    user = request.user
    payload = {
        'profile': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'country': user.country,
            'joined': user.date_joined.isoformat() if user.date_joined else None,
        },
        'devices': [
            {
                'nickname': d.nickname,
                'imei': d.imei,
                'serial_number': d.serial_number,
                'phone_number': d.phone_number,
                'platform': d.platform,
                'status': d.status,
                'registered_at': d.registered_at.isoformat(),
            }
            for d in user.devices.all()
        ],
        'locations': [
            {
                'device': loc.device.nickname,
                'latitude': str(loc.latitude),
                'longitude': str(loc.longitude),
                'recorded_at': loc.recorded_at.isoformat(),
            }
            for loc in DeviceEvent.objects.none()  # placeholder, replace with Location later
        ],
        'events': [
            {
                'device': ev.device.nickname,
                'kind': ev.kind,
                'occurred_at': ev.occurred_at.isoformat(),
            }
            for ev in DeviceEvent.objects.filter(device__owner=user)
        ],
    }
    response = JsonResponse(payload, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = (
        f'attachment; filename="phone-locator-{user.username}.json"'
    )
    return response


@login_required
def settings_delete_account(request):
    """Two-step deletion: confirmation page then actual delete."""
    if request.method == 'POST':
        confirm = request.POST.get('confirm', '').strip()
        if confirm != request.user.username:
            messages.error(
                request,
                'Please type your username exactly to confirm deletion.'
            )
            return redirect('dashboard:settings_delete_account')

        # Log the user out and delete
        from django.contrib.auth import logout
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('dashboard:login')

    return render(request, 'dashboard/settings_delete_account.html')
