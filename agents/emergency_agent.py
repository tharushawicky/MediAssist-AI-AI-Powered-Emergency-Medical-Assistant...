"""Emergency Detection Agent (Google ADK Architecture)."""

from models.ai_response import MANDATORY_DISCLAIMER, EmergencyAssessment
from services.emergency_service import EmergencyService
from services.gemini_service import GeminiService


class EmergencyDetectionAgent:
    """Agent specialized in emergency triage, symptom risk evaluation, and severity level assignment."""

    def __init__(self, gemini_service: GeminiService | None = None):
        self.gemini = gemini_service or GeminiService()
        self.emergency_service = EmergencyService()

    def process(self, symptoms_text: str) -> EmergencyAssessment:
        """Analyze symptoms and return structured emergency assessment."""
        # 1. First run fast rule-based red-flag evaluation
        rule_eval = self.emergency_service.evaluate_emergency(symptoms_text)

        if rule_eval["severity"] == "HIGH":
            return EmergencyAssessment(
                severity="HIGH",
                reason=rule_eval["reason"],
                recommendation=rule_eval["recommendation"],
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 2. If Gemini is available, run prompt for refined AI evaluation
        if self.gemini.is_available:
            prompt = (
                f"Analyze the following patient symptoms for emergency risk level:\n"
                f"Symptoms: {symptoms_text}\n\n"
                f"Assign severity level (LOW, MEDIUM, or HIGH). Explain your reason and recommendation. "
                f"Remember: Chest pain, difficulty breathing, stroke symptoms, or heavy bleeding MUST be assigned HIGH."
            )
            sys_inst = (
                "You are an Emergency Detection AI Agent. Evaluate symptoms carefully. "
                "Output clear assessment with severity, reason, recommendation, and non-diagnosis disclaimer."
            )
            ai_raw = self.gemini.generate_response(prompt, system_instruction=sys_inst)

            # Check if LLM output mentions high or critical indicators
            if "HIGH" in ai_raw.upper() or "EMERGENCY" in ai_raw.upper():
                return EmergencyAssessment(
                    severity=rule_eval["severity"] if rule_eval["severity"] != "LOW" else "HIGH",
                    reason=rule_eval["reason"] if rule_eval["severity"] != "LOW" else "AI detected elevated risk symptoms.",
                    recommendation="Seek immediate emergency medical care or call 911 / 112.",
                    disclaimer=MANDATORY_DISCLAIMER,
                )

        return EmergencyAssessment(
            severity=rule_eval["severity"],
            reason=rule_eval["reason"],
            recommendation=rule_eval["recommendation"],
            disclaimer=MANDATORY_DISCLAIMER,
        )
