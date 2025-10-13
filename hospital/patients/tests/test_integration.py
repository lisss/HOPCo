import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from ..models import Patient, Procedure


@pytest.mark.django_db
class TestPatientIntegration:
    def test_create_patient(self, django_api_client):
        url = reverse("patient-list")
        data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "gender": "F",
            "date_of_birth": "1985-05-15",
        }
        response = django_api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Jane Doe"
        assert response.data["email"] == "jane@example.com"
        assert response.data["gender"] == "F"
        assert "id" in response.data

        Patient.objects.get(id=response.data["id"]).delete()

    def test_retrieve_patient(self, django_api_client, django_patient):
        url = reverse("patient-list")

        response = django_api_client.get(url, {"search": django_patient.email})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        patient_data = response.data["results"][0]
        assert patient_data["name"] == "John Doe"
        assert patient_data["email"] == "john@example.com"

        response = django_api_client.get(url, {"search": django_patient.name})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        patient_data = response.data["results"][0]
        assert patient_data["name"] == "John Doe"
        assert patient_data["email"] == "john@example.com"

    def test_update_patient(self, django_api_client, django_patient):
        search_url = reverse("patient-list")
        search_response = django_api_client.get(search_url, {"search": django_patient.email})
        assert search_response.status_code == status.HTTP_200_OK
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-detail", kwargs={"pk": patient_id})
        data = {
            "name": "Jennifer Wilson",
            "email": "jennifer.wilson@example.com",
            "gender": "F",
            "date_of_birth": "1990-01-01",
        }
        response = django_api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Jennifer Wilson"
        assert response.data["email"] == "jennifer.wilson@example.com"

        django_patient.refresh_from_db()
        assert django_patient.name == "Jennifer Wilson"
        assert django_patient.email == "jennifer.wilson@example.com"

    def test_delete_patient(self, django_api_client):
        patient = Patient.objects.create(
            name="Christopher Lee",
            email="christopher.lee@example.com",
            gender="M",
            date_of_birth="1990-01-01",
        )

        search_url = reverse("patient-list")
        search_response = django_api_client.get(search_url, {"search": patient.email})
        assert search_response.status_code == status.HTTP_200_OK
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-detail", kwargs={"pk": patient_id})
        response = django_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert not Patient.objects.filter(id=patient.pk).exists()

    def test_list_patients(self, django_api_client, django_patient):
        url = reverse("patient-list")
        response = django_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1

    def test_patient_search(self, django_api_client, django_patient):
        url = reverse("patient-list")
        response = django_api_client.get(url, {"search": "john@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1
        assert any(p["email"] == "john@example.com" for p in response.data["results"])

        response = django_api_client.get(url, {"search": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1
        assert any(p["name"] == "John Doe" for p in response.data["results"])

    def test_assign_procedure_to_patient(self, django_api_client, django_patient, django_clinician):
        search_url = reverse("patient-list")
        search_response = django_api_client.get(search_url, {"search": django_patient.email})
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-assign-procedure", kwargs={"pk": patient_id})
        data = {
            "name": "Heart Surgery",
            "date": (timezone.now() + timedelta(days=30)).isoformat(),
            "clinician": django_clinician.pk,
        }
        response = django_api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Heart Surgery"
        assert response.data["patient"] == django_patient.pk
        assert response.data["clinician"] == django_clinician.pk
        assert "date" in response.data

        procedure = Procedure.objects.get(id=response.data["id"])
        assert procedure.date is not None
        assert procedure.clinician == django_clinician
        assert procedure.patient == django_patient

        procedure.delete()

    def test_patient_count_by_department(
        self, django_api_client, department, django_clinician, django_patient
    ):
        django_patient.clinicians.add(django_clinician)
        url = "/api/clinician-patient-counts/by_department/"
        response = django_api_client.get(url, {"department_id": department["id"]})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_patients_by_procedure(self, django_api_client, django_patient, django_clinician):
        procedure = Procedure.objects.create(
            name="Heart Surgery",
            date=timezone.now() + timedelta(days=30),
            patient=django_patient,
            clinician=django_clinician,
        )
        url = "/api/patients/by_procedure/"
        response = django_api_client.get(url, {"procedure_name": "Heart Surgery"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["patient_name"] == "John Doe"

        procedure.delete()

    def test_error_handling_nonexistent_patient(self, django_api_client):
        url = reverse("patient-detail", kwargs={"pk": 99999})
        response = django_api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_error_handling_invalid_data(self, django_api_client):
        url = reverse("patient-list")
        response = django_api_client.post(url, {"name": "Amanda Taylor"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_error_handling_update_nonexistent(self, django_api_client):
        url = reverse("patient-detail", kwargs={"pk": 99999})
        data = {
            "name": "Patricia Anderson",
            "email": "nonexistent@example.com",
            "gender": "M",
            "date_of_birth": "1990-01-01",
        }
        response = django_api_client.put(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_error_handling_delete_nonexistent(self, django_api_client):
        url = reverse("patient-detail", kwargs={"pk": 99999})
        response = django_api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_patients_creation(self, django_api_client, patient_factory):
        patient1 = patient_factory(name="Alice Brown", email="alice@example.com", gender="F")
        patient2 = patient_factory(name="Bob Green", email="bob@example.com", gender="M")
        patient3 = patient_factory(name="Carol White", email="carol@example.com", gender="F")

        url = reverse("patient-list")
        response = django_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 3

        patient_ids = [p["id"] for p in response.data["results"]]
        assert patient1.id in patient_ids
        assert patient2.id in patient_ids
        assert patient3.id in patient_ids

    def test_multiple_procedures_for_patient(
        self, django_api_client, django_patient, clinician_factory, procedure_factory
    ):
        clinician1 = clinician_factory(name="Dr. Adams")
        clinician2 = clinician_factory(name="Dr. Baker")

        proc1 = procedure_factory(name="Blood Test", pat=django_patient, clin=clinician1)
        proc2 = procedure_factory(name="X-Ray", pat=django_patient, clin=clinician2)
        proc3 = procedure_factory(name="MRI Scan", pat=django_patient, clin=clinician1)

        assert django_patient.procedures.count() == 3
        assert proc1.patient == django_patient
        assert proc2.patient == django_patient
        assert proc3.patient == django_patient

        assert proc1.clinician == clinician1
        assert proc2.clinician == clinician2
        assert proc3.clinician == clinician1

        assert proc1.date is not None
        assert proc2.date is not None
        assert proc3.date is not None

        procedures = django_patient.procedures.all()
        assert len(procedures) == 3
        for proc in procedures:
            assert proc.date is not None
            assert proc.clinician is not None

    def test_multiple_departments_and_clinicians(
        self, django_api_client, department_factory, clinician_factory, patient_factory
    ):
        dept1 = department_factory(name="Cardiology")
        dept2 = department_factory(name="Neurology")
        dept3 = department_factory(name="Orthopedics")

        clinician1 = clinician_factory(name="Dr. Heart", dept=dept1)
        clinician2 = clinician_factory(name="Dr. Brain", dept=dept2)
        clinician3 = clinician_factory(name="Dr. Bones", dept=dept3)
        clinician4 = clinician_factory(name="Dr. Pulse", dept=dept1)

        patient1 = patient_factory(name="Patient One", email="p1@example.com")
        patient2 = patient_factory(name="Patient Two", email="p2@example.com")

        patient1.clinicians.add(clinician1, clinician2)
        patient2.clinicians.add(clinician3, clinician4)

        url = "/api/clinician-patient-counts/by_department/"
        response = django_api_client.get(url, {"department_id": dept1.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
