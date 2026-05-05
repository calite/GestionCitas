from django.contrib.auth.models import User
from django.db import models


class Establishment(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    email = models.EmailField()
    auto_confirm = models.BooleanField(default=False)
    interval_minutes = models.PositiveIntegerField(default=30)
    simultaneous_capacity = models.PositiveIntegerField(default=1)
    owners = models.ManyToManyField(User, related_name="owned_establishments", blank=True)


class Service(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField()
    color = models.CharField(max_length=20, default="#3B82F6")


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [(STATUS_PENDING, "Pending"), (STATUS_CONFIRMED, "Confirmed"), (STATUS_CANCELLED, "Cancelled")]

    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=50)


class Availability(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="availabilities")
    weekday = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()


class Block(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="blocks")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255)
