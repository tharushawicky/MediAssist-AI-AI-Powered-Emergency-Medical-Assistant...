"""Symptom Analysis Agent (Google ADK Architecture)."""


from models.ai_response import MANDATORY_DISCLAIMER, SymptomAnalysisResponse
from models.symptom_request import SymptomRequest
from services.emergency_service import EmergencyService
from services.gemini_service import GeminiService
from services.knowledge_service import KnowledgeService


class SymptomAnalysisAgent:
    """Agent responsible for educational symptom evaluation and next-step guidance."""

    def __init__(
        self,
        gemini_service: GeminiService | None = None,
        knowledge_service: KnowledgeService | None = None,
    ):
        self.gemini = gemini_service or GeminiService()
        self.ks = knowledge_service or KnowledgeService()
        self.emergency_service = EmergencyService(self.ks)

    def analyze(self, request: SymptomRequest) -> SymptomAnalysisResponse:
        """Process symptom request and yield educational analysis."""
        # 1. Emergency evaluation first
        triage = self.emergency_service.evaluate_emergency(request.symptoms)
        if triage["severity"] == "HIGH":
            return SymptomAnalysisResponse(
                severity="HIGH",
                possible_conditions=["Emergency Condition Requiring Immediate Evaluation"],
                urgency_level="CRITICAL EMERGENCY - Immediate action required.",
                recommended_next_steps=[
                    "Call emergency services (911 / 112) immediately.",
                    "Do not drive yourself to the hospital if experiencing severe chest pain or dizziness.",
                    "Remain calm and stay with someone who can assist you until help arrives."
                ],
                questions_for_clarification=["Are you currently alone?", "Has emergency services been called?"],
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 2. Match potential educational conditions from knowledge base
        kb_matches = self.ks.search_disease_by_symptom(request.symptoms)
        possible_conditions = [m["condition"] for m in kb_matches[:3]]
        if not possible_conditions:
            possible_conditions = ["General Non-specific Viral / Inflammatory Response"]

        # 3. Utilize Gemini if available for personalized educational insights
        recommended_steps = [
            "Rest and ensure adequate hydration.",
            "Monitor body temperature and symptom progression over the next 24-48 hours.",
            "Schedule an appointment with a primary care doctor if symptoms persist or worsen."
        ]
        clarifying_questions = [
            "Are symptoms constant or do they come and go?",
            "Have you noticed any associated fever, nausea, or rash?"
        ]

        if self.gemini.is_available:
            prompt = (
                f"Patient Profile:\n"
                f"- Age: {request.patient.age}\n"
                f"- Gender: {request.patient.gender}\n"
                f"- Medical History: {request.patient.medical_history or 'None'}\n"
                f"- Current Medications: {request.patient.current_medications or 'None'}\n"
                f"- Symptoms: {request.symptoms}\n"
                f"- Duration: {request.duration}\n\n"
                f"Provide educational information regarding potential non-diagnostic conditions, urgency, "
                f"recommended general next steps, and clarifying questions to discuss with a healthcare provider."
            )
            sys_inst = (
                "You are an educational symptom guide agent. Strictly do NOT diagnose. "
                "Emphasize consulting a qualified doctor. Return clean markdown."
            )
            ai_text = self.gemini.generate_response(prompt, system_instruction=sys_inst)

            # Enrich recommendation with AI output if available
            recommended_steps.append("Review Gemini AI Insights: " + ai_text[:200] + "...")

        return SymptomAnalysisResponse(
            severity=triage["severity"],
            possible_conditions=possible_conditions,
            urgency_level=triage["reason"],
            recommended_next_steps=recommended_steps,
            questions_for_clarification=clarifying_questions,
            disclaimer=MANDATORY_DISCLAIMER,
        )
