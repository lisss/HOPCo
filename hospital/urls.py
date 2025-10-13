from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .patients.views import PatientViewSet, ClinicianPatientCountViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet)
router.register(
    r"clinician-patient-counts", ClinicianPatientCountViewSet, basename="clinician-patient-count"
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
