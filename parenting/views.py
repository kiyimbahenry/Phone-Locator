from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from devices.models import Device
from .models import (
    Child, PairingCode, ScreenTimeRule, ParentingAlert,
)


@login_required
def parenting_home(request):
    children = Child.objects.filter(parent=request.user).select_related('device')

    total_children = children.count()
    paired_children = children.filter(is_paired=True).count()
    unread_alerts = ParentingAlert.objects.filter(
        child__parent=request.user, is_read=False
    ).count()

    rows = []
    for child in children:
        web_blocked_today = child.web_filter_logs.filter(
            blocked_at__date=timezone.now().date()
        ).count()

        top_apps = child.app_usage_logs.filter(
            day=timezone.now().date()
        ).order_by('-total_minutes')[:3]

        rows.append({
            'child': child,
            'web_blocked_today': web_blocked_today,
            'top_apps': top_apps,
        })

    return render(request, 'dashboard/parenting.html', {
        'children': rows,
        'total_children': total_children,
        'paired_children': paired_children,
        'unread_alerts': unread_alerts,
    })


@login_required
def add_child(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        age_group = request.POST.get('age_group', 'teen')
        device_id = request.POST.get('device_id')
        consent = request.POST.get('parental_consent') == 'on'

        if not name:
            messages.error(request, "Please enter the child's name.")
            return redirect('parenting:add_child')

        if not device_id:
            messages.error(request, 'Please choose a device.')
            return redirect('parenting:add_child')

        if not consent:
            messages.error(
                request,
                'You must confirm you are the parent or legal guardian of this child.'
            )
            return redirect('parenting:add_child')

        device = get_object_or_404(Device, pk=device_id, owner=request.user)

        if Child.objects.filter(device=device).exists():
            messages.error(request, 'That device is already linked to a child.')
            return redirect('parenting:add_child')

        child = Child.objects.create(
            parent=request.user,
            device=device,
            name=name,
            age_group=age_group,
            parental_consent_given=True,
            parental_consent_at=timezone.now(),
        )

        ScreenTimeRule.objects.get_or_create(child=child)

        messages.success(
            request,
            f'{child.name} added. Now generate a pairing code to link their phone.'
        )
        return redirect('parenting:child_detail', pk=child.pk)

    available_devices = Device.objects.filter(owner=request.user)
    return render(request, 'dashboard/parenting_add_child.html', {
        'available_devices': available_devices,
    })


@login_required
def child_detail(request, pk):
    child = get_object_or_404(Child, pk=pk, parent=request.user)

    today = timezone.now().date()
    usage_today = child.app_usage_logs.filter(day=today).order_by('-total_minutes')
    web_blocked_today = child.web_filter_logs.filter(blocked_at__date=today)
    rules = child.app_rules.all()
    screen_rule = getattr(child, 'screen_time_rule', None)
    alerts = child.alerts.order_by('-occurred_at')[:20]
    latest_location = child.device.locations.order_by('-recorded_at').first()

    return render(request, 'dashboard/parenting_child.html', {
        'child': child,
        'usage_today': usage_today,
        'web_blocked_today': web_blocked_today,
        'rules': rules,
        'screen_rule': screen_rule,
        'alerts': alerts,
        'latest_location': latest_location,
    })


@login_required
def generate_pairing(request, pk):
    child = get_object_or_404(Child, pk=pk, parent=request.user)

    if request.method == 'POST':
        # Invalidate existing unused codes
        PairingCode.objects.filter(child=child, used_at__isnull=True).update(
            used_at=timezone.now()
        )

        code = PairingCode.objects.create(
            child=child,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        messages.success(request, f'New pairing code: {code.code}')
        return redirect('parenting:child_detail', pk=child.pk)

    # GET: show the existing valid code or generate a new one
    existing = PairingCode.objects.filter(
        child=child,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).first()

    if not existing:
        existing = PairingCode.objects.create(
            child=child,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

    return render(request, 'dashboard/parenting_pair.html', {
        'child': child,
        'code': existing,
    })
