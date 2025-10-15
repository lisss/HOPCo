import uuid
from datetime import datetime, timedelta


class TestPatientAPI:
    def test_create_patient(self, client, base_url):
        email = f"sarah.johnson.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Sarah Johnson",
            "email": email,
            "gender": "F",
            "date_of_birth": "1985-05-15",
        }
        response = client.post(f"{base_url}/patients/", json=data)
        assert response.status_code == 201
        patient_data = response.json()
        assert patient_data["name"] == "Sarah Johnson"
        assert patient_data["email"] == email

    def test_retrieve_patient(self, client, base_url):
        email = f"emma.thompson.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Emma Thompson",
            "email": email,
            "gender": "F",
            "date_of_birth": "1988-03-15",
        }
        response = client.post(f"{base_url}/patients/", json=data)
        patient_id = response.json()["id"]

        response = client.get(f"{base_url}/patients/{patient_id}/")
        assert response.status_code == 200
        patient_data = response.json()
        assert patient_data["name"] == "Emma Thompson"
        assert patient_data["email"] == email

    def test_update_patient(self, client, base_url):
        email = f"michael.brown.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Michael Brown",
            "email": email,
            "gender": "M",
            "date_of_birth": "1990-01-01",
        }
        response = client.post(f"{base_url}/patients/", json=data)
        patient_id = response.json()["id"]

        update_data = {
            "name": "Michael Brown",
            "email": email,
            "gender": "M",
            "date_of_birth": "1990-01-01",
        }
        response = client.put(f"{base_url}/patients/{patient_id}/", json=update_data)
        assert response.status_code == 200
        updated_patient = response.json()
        assert updated_patient["email"] == email

    def test_delete_patient(self, client, base_url):
        email = f"robert.wilson.{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "name": "Robert Wilson",
            "email": email,
            "gender": "M",
            "date_of_birth": "1990-01-01",
        }
        response = client.post(f"{base_url}/patients/", json=data)
        patient_id = response.json()["id"]

        response = client.delete(f"{base_url}/patients/{patient_id}/")
        assert response.status_code == 204

        response = client.get(f"{base_url}/patients/{patient_id}/")
        assert response.status_code == 404

    def test_patients_by_procedure(self, client, base_url, patient, clinician):
        assign_url = f"{base_url}/patients/{patient.id}/assign_procedure/"

        procedure1_data = {
            "name": "Heart Surgery",
            "date": (datetime.now() + timedelta(days=30)).isoformat() + "Z",
            "clinician": clinician.id,
        }
        response = client.post(assign_url, json=procedure1_data)
        assert response.status_code == 201

        procedure2_data = {
            "name": "Blood Test",
            "date": (datetime.now() + timedelta(days=15)).isoformat() + "Z",
            "clinician": clinician.id,
        }
        response = client.post(assign_url, json=procedure2_data)
        assert response.status_code == 201

        procedure3_data = {
            "name": "X-Ray",
            "date": (datetime.now() + timedelta(days=45)).isoformat() + "Z",
            "clinician": clinician.id,
        }
        response = client.post(assign_url, json=procedure3_data)
        assert response.status_code == 201

        url = f"{base_url}/patients/by_procedure/"
        response = client.get(url, params={"procedure_name": "Heart Surgery"})
        assert response.status_code == 200
        results = response.json()

        test_patient_result = None
        for patient_result in results:
            if patient_result["patient_id"] == patient.id:
                test_patient_result = patient_result
                break

        assert test_patient_result is not None
        assert test_patient_result["patient_name"] == patient.name
        assert len(test_patient_result["procedures"]) >= 1
        assert test_patient_result["procedures"][0]["procedure_name"] == "Heart Surgery"

    def test_error_handling(self, client, base_url):
        response = client.get(f"{base_url}/patients/99999/")
        assert response.status_code == 404

        response = client.post(f"{base_url}/patients/", json={"name": "Emily Davis"})
        assert response.status_code == 400
