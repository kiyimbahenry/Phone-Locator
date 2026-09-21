from django.core.management.base import BaseCommand
from django.utils import timezone
from devices.models import Device
from locations.models import DeviceEvent


class Command(BaseCommand):
    help = "Create a test DeviceEvent for a given device."

    def add_arguments(self, parser):
        parser.add_argument('device_id', type=int)
        parser.add_argument('kind', type=str, help="e.g. power_off, sim_removed, failed_unlock")
        parser.add_argument('--lat', type=float, default=0.3476)
        parser.add_argument('--lng', type=float, default=32.5825)
        parser.add_argument('--battery', type=int, default=45)

    def handle(self, *args, **options):
        device = Device.objects.get(pk=options['device_id'])
        event = DeviceEvent.objects.create(
            device=device,
            kind=options['kind'],
            message=f"Simulated {options['kind']} event.",
            latitude=options['lat'],
            longitude=options['lng'],
            battery_percent=options['battery'],
            occurred_at=timezone.now(),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Created event #{event.pk} for {device.nickname}: {event.get_kind_display()}"
        ))
