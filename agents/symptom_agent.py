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
        """Process symptom request and yield detailed AI-predicted educational analysis."""
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
                detailed_ai_analysis="🚨 **CRITICAL RED FLAG DETECTED:** Symptoms indicate an immediate life-threatening emergency. Proceed to nearest emergency department immediately.",
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
        detailed_analysis = None

        # 3. Use Gemini AI for expert clinical reasoning and detailed disease analysis
        if self.gemini.is_available:
            prompt = (
                f"Patient Profile:\n"
                f"- Age: {request.patient.age}\n"
                f"- Gender: {request.patient.gender}\n"
                f"- Pre-existing Medical History: {request.patient.medical_history or 'None reported'}\n"
                f"- Current Medications: {request.patient.current_medications or 'None reported'}\n"
                f"- Primary Symptoms: {request.symptoms}\n"
                f"- Symptom Duration: {request.duration}\n\n"
                "Act as a world-class educational Medical AI Assistant. Perform an in-depth clinical analysis.\n"
                "Analyze the patient's symptoms considering their age, gender, medical history, and current medications.\n\n"
                "Return a JSON object formatted strictly as follows (no markdown around JSON):\n"
                "{\n"
                '  "detailed_analysis_markdown": "### 🔬 In-Depth Clinical Assessment\\nDetailed markdown analysis explaining physiological mechanisms, risk factors, and clinical context...",\n'
                '  "possible_conditions": [\n'
                '    "Condition Name 1 - Detailed educational rationale based on profile",\n'
                '    "Condition Name 2 - Detailed educational rationale based on profile",\n'
                '    "Condition Name 3 - Detailed educational rationale based on profile"\n'
                '  ],\n'
                '  "urgency_level": "Comprehensive explanation of symptom urgency and risk factors",\n'
                '  "recommended_next_steps": [\n'
                '    "Immediate home care / monitoring step",\n'
                '    "When and where to seek medical evaluation",\n'
                '    "Red flag warning signs to watch for"\n'
                '  ],\n'
                '  "questions_for_clarification": [\n'
                '    "Targeted question 1 to ask physician",\n'
                '    "Targeted question 2 to ask physician"\n'
                '  ]\n'
                "}\n"
            )
            sys_inst = (
                "You are an expert Medical AI Assistant. Provide thorough, accurate, highly detailed educational health analyses. Strictly non-diagnostic."
            )
            raw_ai = self.gemini.generate_response(prompt, system_instruction=sys_inst)

            try:
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
                    if parsed.get("detailed_analysis_markdown"):
                        detailed_analysis = parsed["detailed_analysis_markdown"]
            except Exception as e:
                logger.warning(f"Failed to parse Gemini JSON output: {e}. Output raw: {raw_ai[:150]}")
                detailed_analysis = raw_ai

        return SymptomAnalysisResponse(
            severity=triage["severity"],
            possible_conditions=possible_conditions,
            urgency_level=urgency_level,
            recommended_next_steps=recommended_steps,
            questions_for_clarification=clarifying_questions,
            detailed_ai_analysis=detailed_analysis,
            disclaimer=MANDATORY_DISCLAIMER,
        )
