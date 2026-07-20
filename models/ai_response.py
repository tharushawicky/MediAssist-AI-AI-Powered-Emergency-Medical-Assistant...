"""Pydantic schemas for AI agent responses."""

from pydantic import BaseModel, Field

MANDATORY_DISCLAIMER = (
    "This information is for educational purposes only and is not a substitute for "
    "professional medical advice, diagnosis, or treatment."
)


class EmergencyAssessment(BaseModel):
    """Output schema for Emergency Detection Agent."""

    severity: str = Field(..., description="Severity level: LOW, MEDIUM, or HIGH")
    reason: str = Field(..., description="Explanation of the risk level")
    recommendation: str = Field(..., description="Immediate action recommendation")
    disclaimer: str = Field(default=MANDATORY_DISCLAIMER)


class SymptomAnalysisResponse(BaseModel):
    """Output schema for Symptom Analysis Agent."""

    severity: str = Field(default="LOW", description="Assessed urgency: LOW, MEDIUM, HIGH")
    possible_conditions: list[str] = Field(
        default_factory=list, description="Educational list of possible non-diagnostic conditions"
    )
    urgency_level: str = Field(..., description="Explanation of urgency")
    recommended_next_steps: list[str] = Field(..., description="Step-by-step guidance for the user")
    questions_for_clarification: list[str] = Field(
        default_factory=list, description="Questions to help gather more details"
    )
    disclaimer: str = Field(default=MANDATORY_DISCLAIMER)


class FirstAidResponse(BaseModel):
    """Output schema for First Aid Agent."""

    topic: str = Field(..., description="First aid condition or topic")
    severity: str = Field(default="MEDIUM", description="Condition severity level")
    steps: list[str] = Field(..., description="Ordered first aid steps")
    warnings: list[str] = Field(default_factory=list, description="Safety precautions and don'ts")
    when_to_call_emergency: str = Field(..., description="Red flag indicators to call emergency services")
    disclaimer: str = Field(default=MANDATORY_DISCLAIMER)


class GeneralAIResponse(BaseModel):
    """General AI completion response structure."""

    agent_name: str
    content: str
    severity: str = Field(default="LOW")
    disclaimer: str = Field(default=MANDATORY_DISCLAIMER)
