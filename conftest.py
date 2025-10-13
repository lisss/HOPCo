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
