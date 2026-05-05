from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Appointment, Availability, Establishment, Service
from .serializers import (
    AdminAppointmentUpdateSerializer,
    AdminMeSerializer,
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AvailabilitySerializer,
    BlockSerializer,
    EstablishmentSerializer,
    ServiceSerializer,
)
from .services import get_available_slots


class LoginView(TokenObtainPairView):
    pass


class PublicEstablishmentsView(APIView):
    def get(self, request):
        data = list(Establishment.objects.values("id", "name", "slug"))
        return Response(data)


class PublicServicesView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        est = get_object_or_404(Establishment, slug=self.kwargs["slug"])
        return Service.objects.filter(establishment=est)


class PublicAvailabilityView(APIView):
    def get(self, request, slug):
        est = get_object_or_404(Establishment, slug=slug)
        date_str = request.query_params.get("date")
        service_id = request.query_params.get("service_id")
        if not date_str or not service_id:
            return Response({"detail": "date and service_id are required"}, status=400)
        date = parse_date(date_str)
        service = get_object_or_404(Service, id=service_id, establishment=est)
        return Response(get_available_slots(est, date, service.duration_minutes))


class PublicAppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer

    def create(self, request, *args, **kwargs):
        est = get_object_or_404(Establishment, slug=self.kwargs["slug"])
        serializer = self.get_serializer(data=request.data, context={"establishment": est})
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class AdminMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            ests = list(Establishment.objects.values("id", "name", "slug"))
        else:
            ests = AdminMeSerializer.build_for_user(request.user)["establishments"]
        return Response({"is_superuser": request.user.is_superuser, "establishments": ests})


class AdminAppointmentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Appointment.objects.order_by("start_datetime")
        return Appointment.objects.filter(establishment__owners=self.request.user).order_by("start_datetime")


class AdminAppointmentUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminAppointmentUpdateSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Appointment.objects.all()
        return Appointment.objects.filter(establishment__owners=self.request.user)


class AdminBlockCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlockSerializer


class ServiceAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Service.objects.all()
        return Service.objects.filter(establishment__owners=self.request.user)


class EstablishmentAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EstablishmentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Establishment.objects.all().order_by("name")
        return Establishment.objects.none()

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only superuser can create establishments"}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only superuser can update establishments"}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only superuser can update establishments"}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only superuser can delete establishments"}, status=403)
        return super().destroy(request, *args, **kwargs)


class AvailabilityAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Availability.objects.all().order_by("weekday", "start_time")
        return Availability.objects.filter(establishment__owners=self.request.user).order_by("weekday", "start_time")
