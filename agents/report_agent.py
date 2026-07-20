"""Medical Report Summary Agent (Google ADK Architecture)."""

from models.ai_response import MANDATORY_DISCLAIMER, GeneralAIResponse
from services.gemini_service import GeminiService


class MedicalReportSummaryAgent:
    """Agent that parses, translates, and summarizes medical reports (PDF/TXT)."""

    def __init__(self, gemini_service: GeminiService | None = None):
        self.gemini = gemini_service or GeminiService()

    def summarize_report(self, report_text: str, filename: str = "Uploaded Document") -> GeneralAIResponse:
        """Process extracted medical document text and return simplified patient summary."""
        if not report_text.strip():
            return GeneralAIResponse(
                agent_name="Medical Report Summary Agent",
                content="No readable text content found in the uploaded file.",
                severity="LOW",
                disclaimer=MANDATORY_DISCLAIMER,
            )

        if self.gemini.is_available:
            summary_content = self.gemini.summarize_report(report_text)
            return GeneralAIResponse(
                agent_name="Medical Report Summary Agent",
                content=summary_content,
                severity="LOW",
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # Fallback offline report parsing using pattern matching
        lines = [line.strip() for line in report_text.splitlines() if line.strip()]
        abnormal_keywords = ["high", "low", "abnormal", "positive", "elevated", "out of range", "critical"]
        abnormal_lines = [line for line in lines if any(kw in line.lower() for kw in abnormal_keywords)]

        fallback_summary = (
            f"### Summary for {filename}\n\n"
            f"**Total Document Length:** {len(lines)} lines analyzed.\n\n"
            "**Key Findings Overview:**\n"
            "- Document parsed successfully in educational offline mode.\n"
            "- Key diagnostic and clinical terminology identified.\n\n"
            "**Highlighted Observations / Potential Abnormalities:**\n"
        )
        if abnormal_lines:
            for line in abnormal_lines[:5]:
                fallback_summary += f"- ⚠️ `{line}`\n"
        else:
            fallback_summary += "- No obvious keywords for abnormal values flagged in automated scan.\n"

        fallback_summary += (
            "\n**Recommendation:** Please review this complete document with your doctor for accurate clinical context."
        )

        return GeneralAIResponse(
            agent_name="Medical Report Summary Agent",
            content=fallback_summary,
            severity="LOW",
            disclaimer=MANDATORY_DISCLAIMER,
        )
