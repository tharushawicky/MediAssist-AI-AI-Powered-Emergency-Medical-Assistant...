"""Unit tests for Pydantic models and schemas."""

import pytest
from pydantic import ValidationError

from models.ai_response import MANDATORY_DISCLAIMER, EmergencyAssessment
from models.medicine_model import MedicineQuery
from models.patient import PatientProfile
from models.symptom_request import SymptomRequest


def test_patient_profile_valid():
    p = PatientProfile(age=35, gender="Male", medical_history="Asthma", current_medications="Albuterol")
    assert p.age == 35
    assert p.gender == "Male"


def test_patient_profile_invalid_age():
    with pytest.raises(ValidationError):
        PatientProfile(age=150, gender="Female")


def test_symptom_request_empty_symptoms():
    patient = PatientProfile(age=25, gender="Female")
    with pytest.raises(ValidationError):
        SymptomRequest(patient=patient, symptoms="   ")


def test_emergency_assessment_disclaimer():
    assessment = EmergencyAssessment(
        severity="HIGH",
        reason="Chest pain detected",
        recommendation="Call 911"
    )
    assert assessment.severity == "HIGH"
    assert MANDATORY_DISCLAIMER in assessment.disclaimer


def test_medicine_query_validation():
    with pytest.raises(ValidationError):
        MedicineQuery(query=" ")

    mq = MedicineQuery(query="Paracetamol")
    assert mq.query == "Paracetamol"
