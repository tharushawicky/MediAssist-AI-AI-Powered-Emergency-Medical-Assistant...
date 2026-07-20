"""UI helper functions, custom CSS injection, status badges, and audio TTS generator."""

import base64
import io
import logging

import streamlit as st

logger = logging.getLogger("MediAssistAI.Helpers")


def render_custom_css():
    """Inject modern healthcare custom CSS styling into Streamlit."""
    custom_css = """
    <style>
    /* Global Styling */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Banner */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.25);
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-weight: 800;
        font-size: 2.2rem;
    }
    
    .main-header p {
        color: #E0F2FE;
        margin-top: 0.4rem;
        font-size: 1.05rem;
    }

    /* Cards & Container */
    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Emergency Alert Bar */
    .emergency-alert-high {
        background-color: #FEF2F2;
        border-left: 6px solid #DC2626;
        color: #991B1B;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1.2rem;
        font-weight: 600;
    }

    .emergency-alert-medium {
        background-color: #FFFBEB;
        border-left: 6px solid #D97706;
        color: #92400E;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1.2rem;
    }

    /* Disclaimer Footer Box */
    .disclaimer-box {
        background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        color: #475569;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-top: 1.5rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_severity_badge(severity: str) -> str:
    """Return HTML formatted severity badge."""
    sev = severity.upper()
    if sev == "HIGH":
        return "<span style='background-color:#EF4444; color:white; padding:4px 12px; border-radius:12px; font-weight:bold;'>🔴 HIGH SEVERITY</span>"
    elif sev == "MEDIUM":
        return "<span style='background-color:#F59E0B; color:white; padding:4px 12px; border-radius:12px; font-weight:bold;'>🟡 MEDIUM URGENCY</span>"
    else:
        return "<span style='background-color:#10B981; color:white; padding:4px 12px; border-radius:12px; font-weight:bold;'>🟢 LOW RISK</span>"


def text_to_speech_audio(text: str) -> str:
    """Generate audio HTML player using gTTS or fallback."""
    try:
        from gtts import gTTS
        clean_text = text[:400]  # truncate for fast audio generation
        tts = gTTS(text=clean_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64_audio = base64.b64encode(fp.read()).decode("utf-8")
        return f'<audio controls style="width: 100%; margin-top: 10px;"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>'
    except Exception as e:
        logger.debug(f"gTTS audio generation skipped: {e}")
        return ""
