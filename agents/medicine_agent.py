"""Medicine Information Agent (Google ADK Architecture)."""


from models.ai_response import MANDATORY_DISCLAIMER
from models.medicine_model import MedicineQuery, MedicineResponse
from services.gemini_service import GeminiService
from services.knowledge_service import KnowledgeService


class MedicineInformationAgent:
    """Agent supplying educational pharmaceutical information while strictly refusing dosage prescription."""

    def __init__(
        self,
        knowledge_service: KnowledgeService | None = None,
        gemini_service: GeminiService | None = None,
    ):
        self.ks = knowledge_service or KnowledgeService()
        self.gemini = gemini_service or GeminiService()

    def search_medicine(self, query: MedicineQuery) -> list[MedicineResponse]:
        """Search local KB dataset and return matching medicine information models."""
        matches = self.ks.search_medicine(query.query)
        responses = []

        for item in matches:
            responses.append(
                MedicineResponse(
                    name=item["name"],
                    category=item["category"],
                    uses=item["uses"],
                    common_side_effects=item["common_side_effects"],
                    precautions=item["precautions"],
                    interactions=item["interactions"],
                    dosage_warning=item.get(
                        "dosage_warning",
                        "Avoid providing personalized dosage advice. Consult a doctor or pharmacist."
                    ),
                    disclaimer=MANDATORY_DISCLAIMER,
                )
            )

        if responses:
            return responses

        # Fallback to Gemini for unlisted medicine queries
        if self.gemini.is_available:
            prompt = (
                f"Provide educational information for the medicine: '{query.query}'.\n"
                f"Include category, general uses, common side effects, precautions, and interactions. "
                f"Do NOT provide personalized dosage recommendations."
            )
            sys_inst = (
                "You are a Drug Information Agent. Provide safe, general drug references without dosage advice."
            )
            ai_info = self.gemini.generate_response(prompt, system_instruction=sys_inst)

            return [
                MedicineResponse(
                    name=query.query.capitalize(),
                    category="General Pharmaceutical Reference",
                    uses=ai_info[:250] + "...",
                    common_side_effects=["Consult package insert or healthcare provider."],
                    precautions=[
                        "Do not alter dosage without medical supervision.",
                        "Inform doctor of all current medications to avoid interactions."
                    ],
                    interactions="General drug interactions possible. Consult pharmacist.",
                    dosage_warning="Personalized dosage advice cannot be provided. Please consult a licensed professional.",
                    disclaimer=MANDATORY_DISCLAIMER,
                )
            ]

        return [
            MedicineResponse(
                name=query.query.capitalize(),
                category="Information Not Found in Local Database",
                uses="Medicine record not found in local catalog. Please check spelling or consult a physician.",
                common_side_effects=["N/A"],
                precautions=["Consult a licensed pharmacist or doctor."],
                interactions="N/A",
                dosage_warning="Never self-medicate or guess dosages.",
                disclaimer=MANDATORY_DISCLAIMER,
            )
        ]
