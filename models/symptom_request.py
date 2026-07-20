"""Symptom analysis request model."""


from pydantic import BaseModel, Field, field_validator

from models.patient import PatientProfile


class SymptomRequest(BaseModel):
    """Pydantic payload schema for symptom checking."""

    patient: PatientProfile
    symptoms: str = Field(..., min_length=2, description="Detailed description of symptoms")
    duration: str = Field(default="Not specified", description="Duration of symptoms (e.g., 2 hours, 3 days)")
    additional_notes: str | None = Field(default="", description="Any additional context")

    @field_validator("symptoms")
    @classmethod
    def check_symptoms_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Symptoms description cannot be empty.")
        return cleaned
