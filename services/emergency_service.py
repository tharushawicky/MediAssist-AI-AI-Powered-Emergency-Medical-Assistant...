"""Emergency detection service evaluating red flags and assigning severity levels."""

from typing import Any

from services.knowledge_service import KnowledgeService


class EmergencyService:
    """Service to evaluate emergency risk levels from user input."""

    def __init__(self, knowledge_service: KnowledgeService | None = None):
        self.ks = knowledge_service or KnowledgeService()

    def evaluate_emergency(self, input_text: str) -> dict[str, Any]:
        """Evaluate input for critical red flags and return structured severity assessment."""
        text_lower = input_text.lower().strip()

        high_keywords = self.ks.emergency_keywords.get("high_severity_keywords", [
            "chest pain", "difficulty breathing", "stroke", "heavy bleeding",
            "unconscious", "anaphylaxis", "cardiac arrest", "shortness of breath"
        ])
        medium_keywords = self.ks.emergency_keywords.get("medium_severity_keywords", [
            "burn", "fracture", "snake bite", "high fever", "deep cut", "severe abdominal pain"
        ])

        # Mandatory Red Flag Check
        matched_high = [kw for kw in high_keywords if kw in text_lower]
        if matched_high:
            matched_str = ", ".join(matched_high)
            return {
                "severity": "HIGH",
                "reason": f"Critical emergency symptom detected ({matched_str}). Potential life-threatening cardiac, respiratory, or neurological event.",
                "recommendation": "Call emergency services immediately (911 / 112) or seek urgent emergency medical evaluation at the nearest hospital.",
                "is_emergency": True
            }

        matched_medium = [kw for kw in medium_keywords if kw in text_lower]
        if matched_medium:
            matched_str = ", ".join(matched_medium)
            return {
                "severity": "MEDIUM",
                "reason": f"Moderate urgency symptom detected ({matched_str}). Requires prompt medical evaluation.",
                "recommendation": "Visit an urgent care clinic or consult a physician within 24 hours if symptoms worsen.",
                "is_emergency": False
            }

        return {
            "severity": "LOW",
            "reason": "No immediate life-threatening emergency keywords detected.",
            "recommendation": "Self-monitor symptoms. Consult a primary care physician for routine medical advice.",
            "is_emergency": False
        }
