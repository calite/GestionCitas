from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from apps.core.models import Availability, Establishment, Service


class Command(BaseCommand):
    def handle(self, *args, **options):
        businesses = [
            {
                "slug": "demo",
                "name": "Demo Business",
                "email": "demo@citaflow.local",
                "auto_confirm": True,
                "interval_minutes": 30,
                "simultaneous_capacity": 1,
                "services": [
                    {"name": "Consulta general", "duration_minutes": 60, "color": "#22C55E"},
                ],
                "availability": {"start": "09:00", "end": "17:00", "weekdays": range(0, 5)},
            },
            {
                "slug": "peluqueria",
                "name": "Peluqueria Centro",
                "email": "peluqueria@citaflow.local",
                "auto_confirm": True,
                "interval_minutes": 30,
                "simultaneous_capacity": 2,
                "services": [
                    {"name": "Corte de pelo", "duration_minutes": 30, "color": "#F97316"},
                    {"name": "Coloracion", "duration_minutes": 90, "color": "#EF4444"},
                ],
                "availability": {"start": "10:00", "end": "20:00", "weekdays": range(0, 6)},
            },
            {
                "slug": "taller",
                "name": "Taller Motor Plus",
                "email": "taller@citaflow.local",
                "auto_confirm": False,
                "interval_minutes": 60,
                "simultaneous_capacity": 3,
                "services": [
                    {"name": "Revision general", "duration_minutes": 60, "color": "#3B82F6"},
                    {"name": "Cambio aceite", "duration_minutes": 45, "color": "#0EA5E9"},
                ],
                "availability": {"start": "08:00", "end": "18:00", "weekdays": range(0, 5)},
            },
            {
                "slug": "dentista",
                "name": "Clinica Dental Sonrisa",
                "email": "dentista@citaflow.local",
                "auto_confirm": False,
                "interval_minutes": 30,
                "simultaneous_capacity": 1,
                "services": [
                    {"name": "Limpieza dental", "duration_minutes": 45, "color": "#14B8A6"},
                    {"name": "Empaste", "duration_minutes": 60, "color": "#0D9488"},
                ],
                "availability": {"start": "09:00", "end": "15:00", "weekdays": range(0, 5)},
            },
        ]

        for item in businesses:
            est, _ = Establishment.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "email": item["email"],
                    "auto_confirm": item["auto_confirm"],
                    "interval_minutes": item["interval_minutes"],
                    "simultaneous_capacity": item["simultaneous_capacity"],
                },
            )

            owner_username = f"owner_{est.slug}"
            owner, _ = User.objects.get_or_create(username=owner_username)
            owner.set_password(owner_username)
            owner.is_staff = True
            owner.save()

            est.owners.clear()
            est.owners.add(owner)

            for svc in item["services"]:
                Service.objects.get_or_create(
                    establishment=est,
                    name=svc["name"],
                    defaults={"duration_minutes": svc["duration_minutes"], "color": svc["color"]},
                )

            for weekday in item["availability"]["weekdays"]:
                Availability.objects.get_or_create(
                    establishment=est,
                    weekday=weekday,
                    start_time=item["availability"]["start"],
                    end_time=item["availability"]["end"],
                )

        self.stdout.write("Demo data ready")