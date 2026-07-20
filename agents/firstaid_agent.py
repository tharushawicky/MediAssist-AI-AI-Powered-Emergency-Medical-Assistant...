"""First Aid Assistant Agent (Google ADK Architecture)."""


from models.ai_response import MANDATORY_DISCLAIMER, FirstAidResponse
from services.gemini_service import GeminiService
from services.knowledge_service import KnowledgeService


class FirstAidAgent:
    """Agent that retrieves first aid procedures from JSON KB and Gemini."""

    def __init__(
        self,
        knowledge_service: KnowledgeService | None = None,
        gemini_service: GeminiService | None = None,
    ):
        self.ks = knowledge_service or KnowledgeService()
        self.gemini = gemini_service or GeminiService()

    def get_first_aid_guide(self, user_query: str) -> FirstAidResponse:
        """Retrieve step-by-step first aid instructions for given query."""
        kb_result = self.ks.get_first_aid(user_query)

        if kb_result:
            return FirstAidResponse(
                topic=kb_result.get("title", user_query.capitalize()),
                severity=kb_result.get("severity", "MEDIUM"),
                steps=kb_result.get("steps", []),
                warnings=kb_result.get("warnings", []),
                when_to_call_emergency=kb_result.get(
                    "when_to_call_emergency", "Call emergency services if symptoms worsen or victim loses consciousness."
                ),
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # Fallback to Gemini if query not in standard JSON catalog
        topic_title = user_query.strip().capitalize()
        steps = [
            "Keep the affected person calm and motionless.",
            "Assess the surroundings for danger before approaching.",
            "Apply basic safety measures while awaiting medical assistance."
        ]
        warnings = ["Do not apply unverified home remedies or ice directly to wounds."]
        emergency_trigger = "Call emergency services immediately if the condition deteriorates."

        if self.gemini.is_available:
            prompt = (
                f"Provide concise, step-by-step emergency first aid instructions for: '{user_query}'.\n"
                f"Include safety warnings (what NOT to do) and clear criteria for when to call emergency services."
            )
            sys_inst = (
                "You are an Emergency First Aid Guide Agent. Output structured step-by-step first aid protocols."
            )
            ai_text = self.gemini.generate_response(prompt, system_instruction=sys_inst)
            steps.append("Additional AI Guidance: " + ai_text[:300])

        return FirstAidResponse(
            topic=topic_title,
            severity="MEDIUM",
            steps=steps,
            warnings=warnings,
            when_to_call_emergency=emergency_trigger,
            disclaimer=MANDATORY_DISCLAIMER,
        )
