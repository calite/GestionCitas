from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.utils import timezone
from .models import Appointment, Availability, Block


def has_capacity(establishment, start_dt, end_dt, exclude_id=None):
    qs = Appointment.objects.filter(
        establishment=establishment,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
        start_datetime__lt=end_dt,
        end_datetime__gt=start_dt,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.count() < establishment.simultaneous_capacity


def is_blocked(establishment, start_dt, end_dt):
    return Block.objects.filter(
        establishment=establishment,
        start_datetime__lt=end_dt,
        end_datetime__gt=start_dt,
    ).exists()


def get_available_slots(establishment, date, service_duration):
    weekday = date.weekday()
    ranges = Availability.objects.filter(establishment=establishment, weekday=weekday)
    slots = []
    for r in ranges:
        current = timezone.make_aware(datetime.combine(date, r.start_time))
        range_end = timezone.make_aware(datetime.combine(date, r.end_time))
        step = timedelta(minutes=establishment.interval_minutes)
        dur = timedelta(minutes=service_duration)
        while current + dur <= range_end:
            end_dt = current + dur
            if not is_blocked(establishment, current, end_dt) and has_capacity(establishment, current, end_dt):
                slots.append({"start": current.isoformat(), "end": end_dt.isoformat()})
            current += step
    return slots


def send_appointment_email(appointment):
    send_mail(
        subject=f"New appointment for {appointment.establishment.name}",
        message=f"{appointment.client_name} booked on {appointment.start_datetime}",
        from_email=None,
        recipient_list=[appointment.establishment.email],
        fail_silently=True,
    )
