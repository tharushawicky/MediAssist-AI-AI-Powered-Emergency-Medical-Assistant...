"""Patient profile schema definition."""


from pydantic import BaseModel, Field, field_validator


class PatientProfile(BaseModel):
    """Pydantic model representing patient medical background."""

    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., description="Patient gender (e.g., Male, Female, Other, Prefer not to say)")
    medical_history: str | None = Field(default="", description="Pre-existing medical conditions")
    current_medications: str | None = Field(default="", description="List of current medications")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            return "Unspecified"
        return cleaned
