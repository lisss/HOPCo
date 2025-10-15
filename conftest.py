import pytest
import requests
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return requests.Session()


@pytest.fixture
def base_url():
    return "http://localhost:8000/api"


@pytest.fixture
@pytest.mark.django_db
def department(db):
    from hospital.departments.models import Department

    dept = Department.objects.create(name="Test Cardiology")
    yield {"id": dept.id, "name": dept.name}


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def clinician(department, db):
    from hospital.clinicians.models import Clinician
    from hospital.departments.models import Department

    dept = Department.objects.get(id=department["id"])
    return Clinician.objects.create(name="Dr. Smith", department=dept)


@pytest.fixture
@pytest.mark.django_db
def patient(db):
    from hospital.patients.models import Patient

    return Patient.objects.create(
        name="John Doe", email="john@example.com", gender="M", date_of_birth="1990-01-01"
    )


@pytest.fixture(autouse=True)
def cleanup(request, db):
    from hospital.departments.models import Department
    from hospital.clinicians.models import Clinician
    from hospital.patients.models import Patient, Procedure

    initial_department_ids = set(Department.objects.values_list("id", flat=True))
    initial_clinician_ids = set(Clinician.objects.values_list("id", flat=True))
    initial_patient_ids = set(Patient.objects.values_list("id", flat=True))
    initial_procedure_ids = set(Procedure.objects.values_list("id", flat=True))

    yield

    current_procedure_ids = set(Procedure.objects.values_list("id", flat=True))
    new_procedure_ids = current_procedure_ids - initial_procedure_ids

    for procedure_id in new_procedure_ids:
        try:
            Procedure.objects.filter(id=procedure_id).delete()
        except Exception:
            pass

    current_patient_ids = set(Patient.objects.values_list("id", flat=True))
    new_patient_ids = current_patient_ids - initial_patient_ids

    for patient_id in new_patient_ids:
        try:
            Patient.objects.filter(id=patient_id).delete()
        except Exception:
            pass

    current_clinician_ids = set(Clinician.objects.values_list("id", flat=True))
    new_clinician_ids = current_clinician_ids - initial_clinician_ids

    for clinician_id in new_clinician_ids:
        try:
            Clinician.objects.filter(id=clinician_id).delete()
        except Exception:
            pass

    current_department_ids = set(Department.objects.values_list("id", flat=True))
    new_department_ids = current_department_ids - initial_department_ids

    for department_id in new_department_ids:
        try:
            Department.objects.filter(id=department_id).delete()
        except Exception:
            pass
