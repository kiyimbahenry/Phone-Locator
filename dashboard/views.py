from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from devices.forms import DeviceForm
from devices.models import Device
from locations.models import DeviceEvent


class DashboardLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard:login')


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

    return render(request, 'dashboard/locations.html', {
        'devices': rows,
    })


@login_required
def family_view(request):
    return render(request, 'dashboard/family.html')


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
    return render(request, 'dashboard/settings.html')
