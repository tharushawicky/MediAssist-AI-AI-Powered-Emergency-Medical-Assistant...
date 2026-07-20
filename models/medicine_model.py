"""Medicine lookup request and response models."""

from pydantic import BaseModel, Field, field_validator

from models.ai_response import MANDATORY_DISCLAIMER


class MedicineQuery(BaseModel):
    """Payload model for searching medicine information."""

    query: str = Field(..., min_length=2, description="Medicine name or active ingredient")

    @field_validator("query")
    @classmethod
    def clean_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Medicine query cannot be empty.")
        return cleaned


class MedicineResponse(BaseModel):
    """Detailed response schema for medicine information."""

    name: str = Field(..., description="Medicine brand / generic name")
    category: str = Field(..., description="Pharmacological category")
    uses: str = Field(..., description="General indications and uses")
    common_side_effects: list[str] = Field(..., description="List of common side effects")
    precautions: list[str] = Field(..., description="Safety precautions and warnings")
    interactions: str = Field(..., description="General drug interaction guidance")
    dosage_warning: str = Field(
        default="Avoid providing personalized dosage advice. Consult a healthcare provider."
    )
    disclaimer: str = Field(default=MANDATORY_DISCLAIMER)
