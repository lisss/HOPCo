from django.contrib import admin
from .departments.models import Department
from .clinicians.models import Clinician
from .patients.models import Patient, Procedure


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]


@admin.register(Clinician)
class ClinicianAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "created_at", "updated_at"]
    list_filter = ["department"]
    search_fields = ["name"]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "gender", "date_of_birth", "created_at", "updated_at"]
    list_filter = ["gender", "date_of_birth"]
    search_fields = ["name", "email"]
    filter_horizontal = ["clinicians"]


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ["name", "patient", "clinician", "date", "created_at", "updated_at"]
    list_filter = ["date", "clinician__department"]
    search_fields = ["name", "patient__name", "clinician__name"]
