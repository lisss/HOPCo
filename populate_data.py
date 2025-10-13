import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")
django.setup()

from hospital.departments.models import Department
from hospital.clinicians.models import Clinician
from hospital.patients.models import Patient, Procedure


def cleanup_duplicates():
    for dept_name in ["Cardiology", "Surgery", "Pediatrics", "Emergency", "Radiology"]:
        depts = Department.objects.filter(name=dept_name)
        if depts.count() > 1:
            for dept in depts[1:]:
                dept.delete()
    for clinician_name in [
        "Dr. Smith",
        "Dr. Johnson",
        "Dr. Wilson",
        "Dr. Brown",
        "Dr. Davis",
        "Dr. Miller",
        "Dr. Garcia",
    ]:
        clinicians = Clinician.objects.filter(name=clinician_name)
        if clinicians.count() > 1:
            for clinician in clinicians[1:]:
                clinician.delete()


def populate_data():
    cleanup_duplicates()
    departments = [
        {"name": "Cardiology"},
        {"name": "Surgery"},
        {"name": "Pediatrics"},
        {"name": "Emergency"},
        {"name": "Radiology"},
    ]
    for dept_data in departments:
        dept = Department.objects.filter(name=dept_data["name"]).first()
        if not dept:
            dept = Department.objects.create(name=dept_data["name"])
    clinicians_data = [
        {"name": "Dr. Smith", "department": "Cardiology"},
        {"name": "Dr. Johnson", "department": "Cardiology"},
        {"name": "Dr. Wilson", "department": "Surgery"},
        {"name": "Dr. Brown", "department": "Surgery"},
        {"name": "Dr. Davis", "department": "Pediatrics"},
        {"name": "Dr. Miller", "department": "Emergency"},
        {"name": "Dr. Garcia", "department": "Radiology"},
    ]
    for clinician_data in clinicians_data:
        department = Department.objects.filter(name=clinician_data["department"]).first()
        if not department:
            continue
        clinician = Clinician.objects.filter(
            name=clinician_data["name"], department=department
        ).first()
        if not clinician:
            clinician = Clinician.objects.create(name=clinician_data["name"], department=department)
    patients_data = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "gender": "M",
            "date_of_birth": "1990-01-01",
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "gender": "F",
            "date_of_birth": "1985-05-15",
        },
        {
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "gender": "M",
            "date_of_birth": "1978-12-03",
        },
        {
            "name": "Alice Brown",
            "email": "alice@example.com",
            "gender": "F",
            "date_of_birth": "1992-08-20",
        },
        {
            "name": "Charlie Wilson",
            "email": "charlie@example.com",
            "gender": "M",
            "date_of_birth": "1988-03-10",
        },
        {
            "name": "Diana Davis",
            "email": "diana@example.com",
            "gender": "F",
            "date_of_birth": "1995-11-25",
        },
    ]
    for patient_data in patients_data:
        patient = Patient.objects.filter(email=patient_data["email"]).first()
        if not patient:
            patient = Patient.objects.create(**patient_data)
    try:
        john = Patient.objects.filter(name="John Doe").first()
        jane = Patient.objects.filter(name="Jane Smith").first()
        bob = Patient.objects.filter(name="Bob Johnson").first()
        alice = Patient.objects.filter(name="Alice Brown").first()
        dr_smith = Clinician.objects.filter(name="Dr. Smith").first()
        dr_johnson = Clinician.objects.filter(name="Dr. Johnson").first()
        dr_wilson = Clinician.objects.filter(name="Dr. Wilson").first()
        dr_davis = Clinician.objects.filter(name="Dr. Davis").first()
        if john and dr_smith:
            john.clinicians.add(dr_smith)
        if jane and dr_smith and dr_johnson:
            jane.clinicians.add(dr_smith, dr_johnson)
        if bob and dr_wilson:
            bob.clinicians.add(dr_wilson)
        if alice and dr_davis:
            alice.clinicians.add(dr_davis)
    except Exception:
        pass
    procedures_data = [
        {
            "name": "Heart Surgery",
            "patient": "John Doe",
            "clinician": "Dr. Smith",
            "date": "2024-12-15T10:00:00Z",
        },
        {
            "name": "Checkup",
            "patient": "Jane Smith",
            "clinician": "Dr. Johnson",
            "date": "2024-12-01T14:30:00Z",
        },
        {
            "name": "Appendectomy",
            "patient": "Bob Johnson",
            "clinician": "Dr. Wilson",
            "date": "2024-12-30T08:00:00Z",
        },
        {
            "name": "X-Ray",
            "patient": "Alice Brown",
            "clinician": "Dr. Davis",
            "date": "2024-11-25T16:00:00Z",
        },
        {
            "name": "Heart Surgery",
            "patient": "Jane Smith",
            "clinician": "Dr. Smith",
            "date": "2025-01-15T09:30:00Z",
        },
        {
            "name": "Consultation",
            "patient": "Charlie Wilson",
            "clinician": "Dr. Miller",
            "date": "2024-12-05T11:15:00Z",
        },
    ]
    for proc_data in procedures_data:
        patient = Patient.objects.filter(name=proc_data["patient"]).first()
        clinician = Clinician.objects.filter(name=proc_data["clinician"]).first()
        if not patient or not clinician:
            continue
        procedure = Procedure.objects.filter(
            name=proc_data["name"], patient=patient, clinician=clinician
        ).first()
        if not procedure:
            procedure = Procedure.objects.create(
                name=proc_data["name"], patient=patient, clinician=clinician, date=proc_data["date"]
            )


if __name__ == "__main__":
    populate_data()
