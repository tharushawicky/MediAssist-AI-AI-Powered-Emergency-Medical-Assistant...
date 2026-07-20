"""Gemini API wrapper service handling completions, chat, rate limits, and fallback modes."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("MediAssistAI.GeminiService")


class GeminiService:
    """Service wrapper for interacting with Google Gemini API with fallback capabilities."""

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-1.5-flash"):
        st_key = None
        try:
            import streamlit as st
            st_key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None
        except Exception:
            st_key = None

        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or st_key
        self.model_name = model_name
        self.client = None
        self.is_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Attempts to initialize Google GenAI or GenerativeAI client."""
        if not self.api_key or self.api_key == "your_google_gemini_api_key_here":
            logger.warning("No valid GEMINI_API_KEY found. Operating in Knowledge-Base Demo Mode.")
            self.is_available = False
            return

        # Try google.genai (new SDK) first, then fallback to google.generativeai
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.is_available = True
            self.sdk_type = "genai"
            logger.info("Initialized Google GenAI SDK client.")
            return
        except Exception as e:
            logger.debug(f"google-genai SDK init failed: {e}. Trying google.generativeai...")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.is_available = True
            self.sdk_type = "generativeai"
            logger.info("Initialized google.generativeai SDK client.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini SDKs: {e}")
            self.is_available = False

    def generate_response(
        self, prompt: str, system_instruction: str | None = None, temperature: float = 0.2
    ) -> str:
        """Generate a response using Gemini, or return fallback response if unavailable."""
        if not self.is_available:
            return self._generate_fallback(prompt)

        try:
            if self.sdk_type == "genai":
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"System Instruction: {system_instruction}\n\nUser Prompt: {prompt}"
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                )
                return response.text if response and hasattr(response, "text") else ""

            elif self.sdk_type == "generativeai":
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"{system_instruction}\n\n{prompt}"
                response = self.client.generate_content(full_prompt)
                return response.text if response and hasattr(response, "text") else ""

        except Exception as e:
            logger.error(f"Gemini API execution error: {e}")
            return self._generate_fallback(prompt)

        return self._generate_fallback(prompt)

    def summarize_report(self, report_text: str) -> str:
        """Summarize a medical report using Gemini."""
        prompt = (
            "Summarize the following medical document in clear, patient-friendly terms. "
            "Highlight key findings, translate complex medical jargon, and list any abnormal lab values. "
            "End with a clear advice to review these results with their doctor.\n\n"
            f"Medical Document:\n{report_text}"
        )
        sys_inst = (
            "You are a medical document analyzer. Provide safe, non-diagnostic educational summaries."
        )
        return self.generate_response(prompt, system_instruction=sys_inst)

    def chat(self, history: list[dict[str, str]], user_message: str) -> str:
        """Conduct a multi-turn chat conversation using Gemini."""
        formatted_prompt = ""
        for msg in history[-6:]:  # include recent context window
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_prompt += f"{role.capitalize()}: {content}\n"
        formatted_prompt += f"User: {user_message}\nAssistant:"

        return self.generate_response(formatted_prompt)

    def _generate_fallback(self, prompt: str) -> str:
        """Return structured local fallback response when offline or API key is absent."""
        lower_prompt = prompt.lower()
        if "chest pain" in lower_prompt or "breathing" in lower_prompt or "stroke" in lower_prompt:
            return (
                "🔴 **HIGH SEVERITY ALERT**\n\n"
                "The symptoms described indicate a potential medical emergency (cardiac or respiratory risk).\n"
                "**Recommendation:** Please call emergency services (911 / 112) or proceed to the nearest emergency room immediately.\n\n"
                "*This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.*"
            )

        return (
            "Based on available educational health guidelines, please stay well-hydrated, monitor symptoms closely, "
            "and rest. If symptoms worsen, persist beyond a few days, or cause significant discomfort, consult a qualified medical doctor.\n\n"
            "*This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.*"
        )
