"""Symptom Analysis Agent (Google ADK Architecture)."""

import json
import logging

from models.ai_response import MANDATORY_DISCLAIMER, SymptomAnalysisResponse
from models.symptom_request import SymptomRequest
from services.emergency_service import EmergencyService
from services.gemini_service import GeminiService
from services.knowledge_service import KnowledgeService

logger = logging.getLogger("MediAssistAI.SymptomAgent")


class SymptomAnalysisAgent:
    """Agent responsible for educational symptom evaluation and next-step guidance using Gemini AI."""

    def __init__(
        self,
        gemini_service: GeminiService | None = None,
        knowledge_service: KnowledgeService | None = None,
    ):
        self.gemini = gemini_service or GeminiService()
        self.ks = knowledge_service or KnowledgeService()
        self.emergency_service = EmergencyService(self.ks)

    def analyze(self, request: SymptomRequest) -> SymptomAnalysisResponse:
        """Process symptom request and yield AI-predicted educational analysis."""
        # 1. Emergency evaluation first
        triage = self.emergency_service.evaluate_emergency(request.symptoms)
        if triage["severity"] == "HIGH":
            return SymptomAnalysisResponse(
                severity="HIGH",
                possible_conditions=["Critical Emergency Condition Requiring Immediate Evaluation"],
                urgency_level="CRITICAL EMERGENCY - Immediate medical intervention required.",
                recommended_next_steps=[
                    "Call emergency services (911 / 112) immediately.",
                    "Do not drive yourself if experiencing severe chest pain, shortness of breath, or numbness.",
                    "Remain calm and stay with someone until emergency responders arrive.",
                ],
                questions_for_clarification=["Has emergency services been dispatched?", "Are you currently alone?"],
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 2. Defaults from local knowledge base
        kb_matches = self.ks.search_disease_by_symptom(request.symptoms)
        possible_conditions = [f"{m['condition']} (Potential Match)" for m in kb_matches[:3]]
        if not possible_conditions:
            possible_conditions = ["Non-specific Viral / Inflammatory Response"]

        urgency_level = triage["reason"]
        recommended_steps = [
            "Rest, maintain good hydration, and monitor temperature.",
            "Track symptom changes closely over the next 24-48 hours.",
            "Consult a licensed medical doctor if symptoms persist or worsen.",
        ]
        clarifying_questions = [
            "Are symptoms continuous or intermittent?",
            "Have you experienced associated fever, nausea, or localized pain?",
        ]

        # 3. Use Gemini AI for dynamic disease prediction & medical analysis
        if self.gemini.is_available:
            prompt = (
                f"Patient Profile:\n"
                f"- Age: {request.patient.age}\n"
                f"- Gender: {request.patient.gender}\n"
                f"- Medical History: {request.patient.medical_history or 'None'}\n"
                f"- Current Medications: {request.patient.current_medications or 'None'}\n"
                f"- Symptoms: {request.symptoms}\n"
                f"- Duration: {request.duration}\n\n"
                "As an advanced health education AI, analyze these specific symptoms and profile.\n"
                "Provide top 3-4 educational potential health conditions/diseases with a brief explanation for each.\n"
                "Respond ONLY with a valid JSON object formatted as follows:\n"
                "{\n"
                '  "possible_conditions": ["Condition A - Explanation", "Condition B - Explanation"],\n'
                '  "urgency_level": "Detailed explanation of urgency",\n'
                '  "recommended_next_steps": ["Step 1", "Step 2", "Step 3"],\n'
                '  "questions_for_clarification": ["Question 1", "Question 2"]\n'
                "}\n"
            )
            sys_inst = (
                "You are a Medical AI Educational Assistant. Strictly non-diagnostic. Return clean JSON."
            )
            raw_ai = self.gemini.generate_response(prompt, system_instruction=sys_inst)

            try:
                # Clean codeblock wrappers if present
                clean_json = raw_ai.strip()
                if clean_json.startswith("```"):
                    clean_json = clean_json.split("```")[1]
                    if clean_json.startswith("json"):
                        clean_json = clean_json[4:]
                clean_json = clean_json.strip()

                parsed = json.loads(clean_json)
                if isinstance(parsed, dict):
                    if parsed.get("possible_conditions"):
                        possible_conditions = parsed["possible_conditions"]
                    if parsed.get("urgency_level"):
                        urgency_level = parsed["urgency_level"]
                    if parsed.get("recommended_next_steps"):
                        recommended_steps = parsed["recommended_next_steps"]
                    if parsed.get("questions_for_clarification"):
                        clarifying_questions = parsed["questions_for_clarification"]
            except Exception as e:
                logger.warning(f"Failed to parse Gemini JSON output: {e}. Output was: {raw_ai[:100]}...")

        return SymptomAnalysisResponse(
            severity=triage["severity"],
            possible_conditions=possible_conditions,
            urgency_level=urgency_level,
            recommended_next_steps=recommended_steps,
            questions_for_clarification=clarifying_questions,
            disclaimer=MANDATORY_DISCLAIMER,
        )
