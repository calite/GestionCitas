from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.models import Appointment, Availability, Establishment, Service


class MultiTenantIsolationTests(APITestCase):
    def setUp(self):
        self.owner_a = User.objects.create_user(username="owner_a", password="owner_a")
        self.owner_b = User.objects.create_user(username="owner_b", password="owner_b")
        self.superuser = User.objects.create_superuser(
            username="admin_global",
            email="admin@local.test",
            password="admin_global",
        )

        self.est_a = Establishment.objects.create(
            name="Est A",
            slug="est-a",
            email="a@local.test",
            auto_confirm=True,
            interval_minutes=30,
            simultaneous_capacity=1,
        )
        self.est_b = Establishment.objects.create(
            name="Est B",
            slug="est-b",
            email="b@local.test",
            auto_confirm=True,
            interval_minutes=30,
            simultaneous_capacity=1,
        )
        self.est_a.owners.add(self.owner_a)
        self.est_b.owners.add(self.owner_b)

        self.service_a = Service.objects.create(
            establishment=self.est_a,
            name="Service A",
            duration_minutes=30,
            color="#22C55E",
        )
        self.service_b = Service.objects.create(
            establishment=self.est_b,
            name="Service B",
            duration_minutes=30,
            color="#3B82F6",
        )

        self.availability_b = Availability.objects.create(
            establishment=self.est_b,
            weekday=1,
            start_time="09:00",
            end_time="12:00",
        )

        start_b = timezone.now() + timedelta(days=1)
        self.appointment_b = Appointment.objects.create(
            establishment=self.est_b,
            service=self.service_b,
            start_datetime=start_b,
            end_datetime=start_b + timedelta(minutes=30),
            status=Appointment.STATUS_PENDING,
            client_name="Cliente B",
            client_phone="600000000",
        )

    def _auth(self, username, password):
        res = self.client.post(
            "/api/auth/login",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_owner_only_sees_own_establishment_in_admin_me(self):
        self._auth("owner_a", "owner_a")
        res = self.client.get("/api/admin/me")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_superuser"])
        self.assertEqual(len(res.data["establishments"]), 1)
        self.assertEqual(res.data["establishments"][0]["id"], self.est_a.id)

    def test_owner_only_sees_own_services(self):
        self._auth("owner_a", "owner_a")
        res = self.client.get("/api/admin/services/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in res.data}
        self.assertEqual(ids, {self.service_a.id})

    def test_owner_cannot_create_service_for_other_establishment(self):
        self._auth("owner_a", "owner_a")
        res = self.client.post(
            "/api/admin/services/",
            {
                "name": "Forbidden service",
                "duration_minutes": 40,
                "color": "#111111",
                "establishment": self.est_b.id,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("establishment", res.data)

    def test_owner_cannot_update_other_establishment_appointment(self):
        self._auth("owner_a", "owner_a")
        res = self.client.patch(
            f"/api/admin/appointments/{self.appointment_b.id}",
            {"status": Appointment.STATUS_CONFIRMED},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_cannot_delete_other_establishment_availability(self):
        self._auth("owner_a", "owner_a")
        res = self.client.delete(f"/api/admin/availability/{self.availability_b.id}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_superuser_sees_all_establishments(self):
        self._auth("admin_global", "admin_global")
        res = self.client.get("/api/admin/me")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_superuser"])
        ids = {item["id"] for item in res.data["establishments"]}
        self.assertEqual(ids, {self.est_a.id, self.est_b.id})

