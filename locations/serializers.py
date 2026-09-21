from rest_framework import serializers
from .models import Location, DeviceEvent


class LocationPingSerializer(serializers.ModelSerializer):
    """
    Used by the DEVICE app to upload a location.
    The device is inferred from the authenticated user,
    so we don't accept `device` from the client here.
    """
    class Meta:
        model = Location
        fields = (
            'latitude', 'longitude', 'accuracy_m',
            'altitude_m', 'speed_mps', 'heading_deg',
            'source', 'battery_percent', 'network_operator',
            'recorded_at',
        )

    def validate_latitude(self, value):
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError('Latitude must be between -90 and 90.')
        return value

    def validate_longitude(self, value):
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError('Longitude must be between -180 and 180.')
        return value

    def validate_battery_percent(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError('Battery must be 0–100.')
        return value


class LocationReadSerializer(serializers.ModelSerializer):
    """
    Used by the DASHBOARD / other users to read a location.
    We include the device id so the client can group by device.
    """
    device_id = serializers.IntegerField(source='device.id', read_only=True)
    device_nickname = serializers.CharField(source='device.nickname', read_only=True)

    class Meta:
        model = Location
        fields = (
            'id', 'device_id', 'device_nickname',
            'latitude', 'longitude', 'accuracy_m',
            'source', 'battery_percent', 'network_operator',
            'recorded_at', 'received_at',
        )


class DeviceEventSerializer(serializers.ModelSerializer):
    """
    Used by the DEVICE app to report a security event:
    power-off, SIM change, failed unlock, etc.
    """
    class Meta:
        model = DeviceEvent
        fields = (
            'kind', 'message', 'metadata',
            'latitude', 'longitude', 'battery_percent',
            'occurred_at',
        )

    def validate_kind(self, value):
        valid = {c[0] for c in DeviceEvent.Kind.choices}
        if value not in valid:
            raise serializers.ValidationError(f"Unknown event kind: {value}")
        return value
