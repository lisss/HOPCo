from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from .models import Patient, Procedure
from ..clinicians.models import Clinician


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "gender", "email", "date_of_birth", "created_at", "updated_at"]


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "email"]

    @action(detail=True, methods=["post"])
    def assign_procedure(self, request, pk=None):
        patient = self.get_object()
        name = request.data.get("name")
        date = request.data.get("date")
        clinician_id = request.data.get("clinician")

        if not name or not date or not clinician_id:
            return Response(
                {"error": "Missing required fields: name, date, clinician"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            clinician = Clinician.objects.get(id=clinician_id)
        except Clinician.DoesNotExist:
            return Response({"error": "Clinician not found"}, status=status.HTTP_404_NOT_FOUND)

        procedure = Procedure.objects.create(
            name=name, date=date, patient=patient, clinician=clinician
        )
        return Response(
            {
                "id": procedure.id,
                "name": procedure.name,
                "date": procedure.date,
                "patient": procedure.patient.id,
                "clinician": procedure.clinician.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def by_procedure(self, request):
        procedure_name = request.query_params.get("procedure_name")
        if not procedure_name:
            return Response(
                {"error": "procedure_name parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )

        patients = Patient.objects.filter(procedures__name__icontains=procedure_name).distinct()
        result = []
        for patient in patients:
            patient_procedures = []
            for proc in patient.procedures.filter(name__icontains=procedure_name):
                patient_procedures.append(
                    {
                        "procedure_id": proc.id,
                        "procedure_name": proc.name,
                        "procedure_date": proc.date,
                        "clinician_name": proc.clinician.name,
                    }
                )
            result.append(
                {
                    "patient_id": patient.id,
                    "patient_name": patient.name,
                    "gender": patient.gender,
                    "email": patient.email,
                    "date_of_birth": patient.date_of_birth,
                    "procedures": patient_procedures,
                }
            )
        return Response(result)


class ClinicianPatientCountViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"])
    def by_department(self, request):
        department_id = request.query_params.get("department_id")
        if not department_id:
            return Response(
                {"error": "department_id parameter required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            clinicians = Clinician.objects.filter(department_id=department_id)
            if not clinicians.exists():
                return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid department_id"}, status=status.HTTP_400_BAD_REQUEST)

        result = []
        for clinician in clinicians:
            patient_count = clinician.patients.count()
            result.append(
                {
                    "clinician_id": clinician.id,
                    "clinician_name": clinician.name,
                    "department_name": clinician.department.name,
                    "patient_count": patient_count,
                }
            )
        return Response(result)
