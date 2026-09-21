from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from devices.models import Device
from .models import Location, DeviceEvent
from .serializers import (
    LocationPingSerializer,
    LocationReadSerializer,
    DeviceEventSerializer,
)


class LocationPingView(APIView):
    """POST /api/locations/ping/ — a device uploads a new location."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'detail': 'device_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device = Device.objects.get(pk=device_id, owner=request.user)
        except Device.DoesNotExist:
            return Response(
                {'detail': 'Device not found or not yours.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not device.consent_given:
            return Response(
                {'detail': 'This device has not given location consent.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LocationPingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.save(device=device)

        device.last_seen_at = timezone.now()
        device.save(update_fields=['last_seen_at', 'updated_at'])

        return Response(
            LocationReadSerializer(location).data,
            status=status.HTTP_201_CREATED,
        )


class LatestLocationsView(APIView):
    """GET /api/locations/latest/ — latest location per user device."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(owner=request.user)
        payload = []

        for device in devices:
            latest = device.locations.order_by('-recorded_at').first()
            payload.append({
                'device_id': device.id,
                'device_nickname': device.nickname,
                'status': device.status,
                'last_seen_at': device.last_seen_at,
                'location': (
                    LocationReadSerializer(latest).data
                    if latest else None
                ),
            })

        return Response({'devices': payload})


class EventCreateView(APIView):
    """
    POST /api/locations/events/

    Body:
        {
          "device_id": 3,
          "kind": "power_off",
          "message": "...",
          "latitude": 0.3476,
          "longitude": 32.5825,
          "battery_percent": 42,
          "occurred_at": "2026-01-20T22:15:00Z"
        }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'detail': 'device_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device = Device.objects.get(pk=device_id, owner=request.user)
        except Device.DoesNotExist:
            return Response(
                {'detail': 'Device not found or not yours.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DeviceEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(device=device)

        device.last_seen_at = timezone.now()
        device.save(update_fields=['last_seen_at', 'updated_at'])

        return Response(
            {
                'id': event.pk,
                'kind': event.kind,
                'occurred_at': event.occurred_at,
            },
            status=status.HTTP_201_CREATED,
        )
