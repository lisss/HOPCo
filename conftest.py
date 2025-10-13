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
    try:
        dept.delete()
    except Exception:
        pass


@pytest.fixture
@pytest.mark.django_db
def clinician(department, db):
    from hospital.clinicians.models import Clinician
    from hospital.departments.models import Department

    dept = Department.objects.get(id=department["id"])
    clinician = Clinician.objects.create(name="Dr. Test Smith", department=dept)
    yield {"id": clinician.id, "name": clinician.name, "department": dept.id}
    try:
        clinician.delete()
    except Exception:
        pass


@pytest.fixture
def patient(client, base_url):
    data = {
        "name": "Test Patient",
        "email": "test.patient@example.com",
        "gender": "M",
        "date_of_birth": "1990-01-01",
    }
    response = client.post(f"{base_url}/patients/", json=data)
    assert response.status_code == 201
    patient_data = response.json()

    yield patient_data

    try:
        client.delete(f"{base_url}/patients/{patient_data['id']}/")
    except Exception:
        pass


@pytest.fixture
def django_api_client():
    return APIClient()


@pytest.fixture
def department_factory():
    from hospital.departments.models import Department

    created_departments = []

    def _create_department(name=None, **kwargs):
        if name is None:
            name = f"Department {len(created_departments) + 1}"
        dept = Department.objects.create(name=name, **kwargs)
        created_departments.append(dept)
        return dept

    yield _create_department

    for dept in created_departments:
        try:
            dept.delete()
        except Exception:
            pass


@pytest.fixture
@pytest.mark.django_db
def django_clinician(department, db):
    from hospital.clinicians.models import Clinician
    from hospital.departments.models import Department

    dept = Department.objects.get(id=department["id"])
    return Clinician.objects.create(name="Dr. Smith", department=dept)


@pytest.fixture
def clinician_factory(department):
    from hospital.clinicians.models import Clinician
    from hospital.departments.models import Department

    created_clinicians = []

    def _create_clinician(name=None, dept=None, **kwargs):
        if name is None:
            name = f"Dr. Clinician {len(created_clinicians) + 1}"
        if dept is None:
            dept = Department.objects.get(id=department["id"])
        clinician = Clinician.objects.create(name=name, department=dept, **kwargs)
        created_clinicians.append(clinician)
        return clinician

    yield _create_clinician

    for clinician in created_clinicians:
        try:
            clinician.delete()
        except Exception:
            pass


@pytest.fixture
@pytest.mark.django_db
def django_patient(db):
    from hospital.patients.models import Patient

    return Patient.objects.create(
        name="John Doe", email="john@example.com", gender="M", date_of_birth="1990-01-01"
    )


@pytest.fixture
def patient_factory():
    from hospital.patients.models import Patient

    created_patients = []

    def _create_patient(name=None, email=None, gender="M", date_of_birth="1990-01-01", **kwargs):
        if name is None:
            name = f"Patient {len(created_patients) + 1}"
        if email is None:
            email = f"patient{len(created_patients) + 1}@example.com"
        patient = Patient.objects.create(
            name=name, email=email, gender=gender, date_of_birth=date_of_birth, **kwargs
        )
        created_patients.append(patient)
        return patient

    yield _create_patient

    for patient in created_patients:
        try:
            patient.delete()
        except Exception:
            pass


@pytest.fixture
def procedure_factory(django_patient, django_clinician):
    from hospital.patients.models import Procedure
    from django.utils import timezone

    created_procedures = []

    def _create_procedure(name=None, date=None, pat=None, clin=None, **kwargs):
        if name is None:
            name = f"Procedure {len(created_procedures) + 1}"
        if date is None:
            date = timezone.now()
        if pat is None:
            pat = django_patient
        if clin is None:
            clin = django_clinician
        procedure = Procedure.objects.create(
            name=name, date=date, patient=pat, clinician=clin, **kwargs
        )
        created_procedures.append(procedure)
        return procedure

    yield _create_procedure

    for procedure in created_procedures:
        try:
            procedure.delete()
        except Exception:
            pass
