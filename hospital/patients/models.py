from django.db import models
from ..clinicians.models import Clinician


class Patient(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    gender = models.CharField(
        max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")]
    )
    date_of_birth = models.DateField()
    clinicians = models.ManyToManyField(Clinician, related_name="patients", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Procedure(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="procedures")
    clinician = models.ForeignKey(Clinician, on_delete=models.CASCADE, related_name="procedures")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} for {self.patient.name}"
