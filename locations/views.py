from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from devices.models import Device
from .models import Location
from .serializers import LocationPingSerializer, LocationReadSerializer


class LocationPingView(APIView):
    """
    POST /api/locations/ping/

    Body:
        {
          "device_id": 3,
          "latitude": 0.3476,
          "longitude": 32.5825,
          "accuracy_m": 18,
          "source": "gps",
          "battery_percent": 63,
          "network_operator": "MTN",
          "recorded_at": "2026-01-20T12:38:00Z"
        }

    The authenticated user must OWN device_id.
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

        if not device.consent_given:
            return Response(
                {'detail': 'This device has not given location consent.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LocationPingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        location = serializer.save(device=device)

        # bump the device last_seen
        device.last_seen_at = timezone.now()
        device.save(update_fields=['last_seen_at', 'updated_at'])

        return Response(
            LocationReadSerializer(location).data,
            status=status.HTTP_201_CREATED,
        )


class LatestLocationsView(APIView):
    """
    GET /api/locations/latest/

    Returns the latest location for each of the user's devices.
    Devices with no locations yet are returned with location=null.
    """
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
