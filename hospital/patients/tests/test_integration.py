import pytest
import uuid
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from ..models import Patient, Procedure


@pytest.mark.django_db
class TestPatientIntegration:
    def test_create_patient(self, api_client):
        url = reverse("patient-list")
        email = f"jane.doe.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Jane Doe",
            "email": email,
            "gender": "F",
            "date_of_birth": "1985-05-15",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Jane Doe"
        assert response.data["email"] == email
        assert "id" in response.data

    def test_retrieve_patient(self, api_client, patient):
        url = reverse("patient-list")

        response = api_client.get(url, {"search": patient.email})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        patient_data = response.data["results"][0]
        assert patient_data["name"] == "John Doe"
        assert patient_data["email"] == "john@example.com"

        response = api_client.get(url, {"search": patient.name})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        patient_data = response.data["results"][0]
        assert patient_data["name"] == "John Doe"
        assert patient_data["email"] == "john@example.com"

    def test_update_patient(self, api_client, patient):
        search_url = reverse("patient-list")
        search_response = api_client.get(search_url, {"search": patient.email})
        assert search_response.status_code == status.HTTP_200_OK
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-detail", kwargs={"pk": patient_id})
        email = f"jennifer.wilson.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Jennifer Wilson",
            "email": email,
            "gender": "F",
            "date_of_birth": "1990-01-01",
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Jennifer Wilson"
        assert response.data["email"] == email

        patient.refresh_from_db()
        assert patient.name == "Jennifer Wilson"
        assert patient.email == email

    def test_delete_patient(self, api_client):
        email = f"christopher.lee.{uuid.uuid4().hex[:8]}@example.com"
        patient = Patient.objects.create(
            name="Christopher Lee",
            email=email,
            gender="M",
            date_of_birth="1990-01-01",
        )

        search_url = reverse("patient-list")
        search_response = api_client.get(search_url, {"search": patient.email})
        assert search_response.status_code == status.HTTP_200_OK
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-detail", kwargs={"pk": patient_id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert not Patient.objects.filter(id=patient.pk).exists()

    def test_search_patients(self, api_client, patient):
        url = reverse("patient-list")
        response = api_client.get(url, {"search": "john@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1
        assert any(p["email"] == "john@example.com" for p in response.data["results"])

    def test_assign_procedure_to_patient(self, api_client, patient, clinician):
        search_url = reverse("patient-list")
        search_response = api_client.get(search_url, {"search": patient.email})
        patient_id = search_response.data["results"][0]["id"]

        url = reverse("patient-assign-procedure", kwargs={"pk": patient_id})
        data = {
            "name": "Heart Surgery",
            "date": (timezone.now() + timedelta(days=30)).isoformat(),
            "clinician": clinician.pk,
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Heart Surgery"
        assert response.data["patient"] == patient.pk

        procedure = Procedure.objects.get(id=response.data["id"])
        assert procedure.patient == patient
        assert procedure.clinician == clinician

    def patients_by_procedure(self, api_client, patient, clinician):
        procedure = Procedure.objects.create(
            name="Heart Surgery",
            date=timezone.now() + timedelta(days=30),
            patient=patient,
            clinician=clinician,
        )
        url = "/api/patients/by_procedure/"
        response = api_client.get(url, {"procedure_name": "Heart Surgery"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["patient_name"] == "John Doe"

    def patient_count_by_department(self, api_client, department, clinician, patient):
        patient.clinicians.add(clinician)
        url = "/api/clinician-patient-counts/by_department/"
        response = api_client.get(url, {"department_id": department["id"]})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_error_handling(self, api_client):
        url = reverse("patient-detail", kwargs={"pk": 99999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        url = reverse("patient-list")
        response = api_client.post(url, {"name": "Amanda Taylor"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
