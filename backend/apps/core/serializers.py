from django.utils import timezone
from rest_framework import serializers
from .models import Appointment, Availability, Block, Establishment, Service
from .services import has_capacity, is_blocked, send_appointment_email


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

    def validate_establishment(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and not request.user.is_superuser:
            if not value.owners.filter(id=request.user.id).exists():
                raise serializers.ValidationError("Not allowed for this establishment")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


class AdminAppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["service", "start_datetime", "client_name", "client_phone"]

    def validate(self, attrs):
        est = self.context["establishment"]
        service = attrs["service"]
        if service.establishment_id != est.id:
            raise serializers.ValidationError("Service does not belong to establishment")
        start_dt = attrs["start_datetime"]
        end_dt = start_dt + timezone.timedelta(minutes=service.duration_minutes)
        if is_blocked(est, start_dt, end_dt):
            raise serializers.ValidationError("Time blocked")
        if not has_capacity(est, start_dt, end_dt):
            raise serializers.ValidationError("No capacity at selected time")
        attrs["end_datetime"] = end_dt
        attrs["establishment"] = est
        attrs["status"] = Appointment.STATUS_CONFIRMED if est.auto_confirm else Appointment.STATUS_PENDING
        return attrs

    def create(self, validated_data):
        appointment = Appointment.objects.create(**validated_data)
        send_appointment_email(appointment)
        return appointment


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = "__all__"

    def validate_establishment(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and not request.user.is_superuser:
            if not value.owners.filter(id=request.user.id).exists():
                raise serializers.ValidationError("Not allowed for this establishment")
        return value


class AdminMeSerializer(serializers.Serializer):
    establishments = serializers.ListField(child=serializers.DictField())

    @staticmethod
    def build_for_user(user):
        qs = Establishment.objects.filter(owners=user).values("id", "name", "slug")
        return {"establishments": list(qs)}


class EstablishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ["id", "name", "slug", "email", "auto_confirm", "interval_minutes", "simultaneous_capacity"]


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = "__all__"

    def validate_establishment(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and not request.user.is_superuser:
            if not value.owners.filter(id=request.user.id).exists():
                raise serializers.ValidationError("Not allowed for this establishment")
        return value
