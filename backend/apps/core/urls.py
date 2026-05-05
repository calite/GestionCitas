from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AdminAppointmentListView, AdminAppointmentUpdateView, AdminBlockCreateView, AdminMeView, AvailabilityAdminViewSet, EstablishmentAdminViewSet, LoginView, PublicAppointmentCreateView, PublicAvailabilityView, PublicEstablishmentsView, PublicServicesView, ServiceAdminViewSet

router = DefaultRouter()
router.register(r"admin/services", ServiceAdminViewSet, basename="admin-services")
router.register(r"admin/establishments", EstablishmentAdminViewSet, basename="admin-establishments")
router.register(r"admin/availability", AvailabilityAdminViewSet, basename="admin-availability")

urlpatterns = [
    path("auth/login", LoginView.as_view()),
    path("establishments", PublicEstablishmentsView.as_view()),
    path("admin/me", AdminMeView.as_view()),
    path("admin/appointments", AdminAppointmentListView.as_view()),
    path("admin/appointments/<int:pk>", AdminAppointmentUpdateView.as_view()),
    path("admin/blocks", AdminBlockCreateView.as_view()),
    path("", include(router.urls)),
    path("<slug:slug>/services", PublicServicesView.as_view()),
    path("<slug:slug>/availability", PublicAvailabilityView.as_view()),
    path("<slug:slug>/appointments", PublicAppointmentCreateView.as_view()),
]
