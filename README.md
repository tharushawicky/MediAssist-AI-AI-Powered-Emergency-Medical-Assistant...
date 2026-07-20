# 🩺 MediAssist AI – AI-Powered Emergency Medical Assistant

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit Framework](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4.svg)](https://deepmind.google/technologies/gemini/)
[![Google ADK Patterns](https://img.shields.io/badge/Google_ADK-Agent_Architecture-34A853.svg)](https://github.com/google)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.7%2B-E92063.svg)](https://docs.pydantic.dev/)
[![Code Style: Ruff](https://img.shields.io/badge/Code_Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)

**MediAssist AI** is a production-quality, AI-powered Emergency Medical Assistant web application built for the **Google Developer Groups (GDG) AI Buildathon**. Leveraging **Google Gemini** and **Google Agent Development Kit (ADK)** design patterns, MediAssist AI provides educational health guidance, immediate emergency triage assessment, step-by-step first-aid protocols, drug safety reference, and medical document summarization.

---

> [!IMPORTANT]
> **MANDATORY MEDICAL DISCLAIMER**
> **MediAssist AI does NOT diagnose medical conditions, prescribe treatments, or replace healthcare professionals.** 
> Every response produced by MediAssist AI explicitly emphasizes its non-diagnostic, educational nature and directs users to seek immediate professional medical attention or call emergency services (**911 / 112**) in high-severity situations.

---

## 🌟 Key Features

1. **🚨 Emergency Detection Agent (`emergency_agent.py`)**
   - Automatically triages symptoms into **🟢 Low**, **🟡 Medium**, or **🔴 High** severity levels.
   - Instantly flags life-threatening red-flag symptoms (*chest pain, difficulty breathing, stroke indicators, severe uncontrolled bleeding*) as **🔴 HIGH** and provides emergency call directives.

2. **🤒 Symptom Analysis Agent (`symptom_agent.py`)**
   - Evaluates patient profile (age, gender, medical history, current medications, symptom duration).
   - Generates educational possible conditions (non-diagnostic), urgency levels, recommended next steps, and clarifying questions to ask a doctor.

3. **🩹 First Aid Assistant Agent (`firstaid_agent.py`)**
   - Instant step-by-step instructions for critical situations (*burns, snake bites, heavy bleeding, fractures, poisoning, CPR, choking, heat stroke*).
   - Highlights critical **Safety Warnings** (e.g., *"Do NOT apply ice to burns"*) and emergency triggers.
   - Built-in **Text-to-Speech (TTS)** voice player for hands-free emergency listening.

4. **💊 Medicine Information Agent (`medicine_agent.py`)**
   - Queries catalog of common pharmaceuticals using **Pandas**.
   - Displays general uses, common side effects, precautions, and drug interactions.
   - Refuses to provide personalized dosage advice to prevent self-medication risks.

5. **📄 Medical Report Summary Agent (`report_agent.py`)**
   - Upload PDF or TXT clinical lab reports and test results.
   - Summarizes complex medical jargon into patient-friendly language and highlights abnormal lab values.

6. **📜 Persistent Chat History & Export**
   - Stores interactions in a local **SQLite** database (`mediassist_chat.db`).
   - Supports filtering by agent type, clearing history, and exporting complete transcripts as **JSON** or **Text**.

7. **⚡ Offline Knowledge-Base Fallback**
   - If `GEMINI_API_KEY` is unavailable, MediAssist AI gracefully falls back to local JSON datasets (`data/*.json`) so evaluators can test the complete interface and workflows without requiring an API key.

---

## 🏗️ Project Architecture

```
mediassist-ai/
│
├── app.py                      # Main Streamlit Web Application Dashboard
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Documentation & Hackathon Showcase
├── .env.example                # Environment Variables Configuration Template
├── ruff.toml                   # Ruff Linter & Formatter Configuration
│
├── agents/                     # Independent AI Agents (Google ADK Architecture)
│   ├── __init__.py
│   ├── emergency_agent.py      # Triage & Emergency Risk Detection Agent
│   ├── symptom_agent.py        # Symptom Analysis & Educational Guidance Agent
│   ├── firstaid_agent.py       # Interactive First Aid Guide Agent
│   ├── medicine_agent.py       # Medicine Reference & Safety Agent
│   └── report_agent.py         # Medical Report (PDF/TXT) Summarization Agent
│
├── services/                   # Business & API Service Layer
│   ├── __init__.py
│   ├── gemini_service.py       # Gemini API client wrapper with retry & fallback handling
│   ├── knowledge_service.py    # JSON Knowledge Base & Pandas dataset query service
│   ├── emergency_service.py    # Rule-based red-flag keyword detection engine
│   └── db_service.py           # SQLite & JSON Chat History persistence service
│
├── models/                     # Pydantic Schemas & Data Models
│   ├── __init__.py
│   ├── patient.py              # Patient profile & history model
│   ├── symptom_request.py      # Symptom request validation schema
│   ├── ai_response.py          # Structured AI response & emergency assessment models
│   └── medicine_model.py       # Medicine query & reference response model
│
├── data/                       # Knowledge Base JSON Datasets
│   ├── emergency_keywords.json # Red-flag symptoms & severity triggers
│   ├── first_aid.json          # First aid procedures, steps & safety warnings
│   ├── medicines.json          # Drug reference catalog (uses, warnings, side effects)
│   ├── diseases.json           # Educational symptom-to-condition mapping
│   └── disclaimer.json         # Mandatory medical disclaimer templates
│
├── utils/                      # Utilities & UI Helpers
│   ├── __init__.py
│   ├── prompts.py              # Agent system prompts with mandatory disclaimers
│   ├── validators.py           # Input sanitization & PDF text extractor
│   └── helpers.py              # Streamlit CSS, severity badges & TTS generator
│
├── tests/                      # Pytest Automated Test Suite
│   ├── __init__.py
│   ├── test_agents.py          # Agent behavior & severity tests
│   ├── test_models.py          # Pydantic schema validation tests
│   ├── test_services.py        # Service layer & fallback tests
│   └── test_knowledge.py       # Knowledge retrieval & search tests
│
└── .streamlit/
    └── config.toml             # Custom Healthcare Theme (Navy/Teal/White)
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.12+**
- **Git**

### 2. Clone Repository & Environment Setup
```bash
git clone https://github.com/your-repo/mediassist-ai.git
cd mediassist-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and add your **Google Gemini API Key**:
```bash
cp .env.example .env
```
In `.env`:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
```
*(Note: If no API key is provided, the application will run seamlessly in Demo Offline Mode).*

---

## 🚀 Running the Application

To start the Streamlit web dashboard:
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🧪 Running Automated Tests & Linting

### Run Pytest Suite
```bash
python -m pytest tests/ -v
```

### Run Ruff Linter
```bash
ruff check .
```

---

## 📜 Future Enhancements
- 🎙️ Full WebRTC Real-time Voice Chat integration using Gemini Multimodal Live API.
- 🌍 Multi-language localization (Spanish, French, Hindi, Mandarain).
- 🏥 Geo-location integration to display nearby open emergency rooms and pharmacies.

---

## 📄 License & Attribution
MediAssist AI is open-source under the MIT License. Built for the Google Developer Groups AI Buildathon showcasing Google Gemini & Google ADK.
