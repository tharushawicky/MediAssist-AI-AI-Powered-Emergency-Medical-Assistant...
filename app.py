"""MediAssist AI - Main Streamlit Web Application."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MediAssist AI - Emergency Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports after page_config
from agents import (
    EmergencyDetectionAgent,
    FirstAidAgent,
    MedicalReportSummaryAgent,
    MedicineInformationAgent,
    SymptomAnalysisAgent,
)
from models import MedicineQuery, PatientProfile, SymptomRequest
from services import ChatDatabaseService, GeminiService, KnowledgeService
from utils import (
    extract_text_from_file,
    render_custom_css,
    render_severity_badge,
    text_to_speech_audio,
)

# Inject Custom CSS
render_custom_css()

# Initialize Services & Agents (Cached in session)
@st.cache_resource
def get_services():
    gemini_svc = GeminiService()
    ks_svc = KnowledgeService()
    db_svc = ChatDatabaseService()

    emergency_agent = EmergencyDetectionAgent(gemini_svc)
    symptom_agent = SymptomAnalysisAgent(gemini_svc, ks_svc)
    firstaid_agent = FirstAidAgent(ks_svc, gemini_svc)
    medicine_agent = MedicineInformationAgent(ks_svc, gemini_svc)
    report_agent = MedicalReportSummaryAgent(gemini_svc)

    return {
        "gemini": gemini_svc,
        "ks": ks_svc,
        "db": db_svc,
        "emergency_agent": emergency_agent,
        "symptom_agent": symptom_agent,
        "firstaid_agent": firstaid_agent,
        "medicine_agent": medicine_agent,
        "report_agent": report_agent,
    }

svcs = get_services()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/medical-heart.png", width=64)
    st.title("MediAssist AI")
    st.caption("AI-Powered Emergency Health Assistant")

    nav_option = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🤒 Symptom Checker",
            "🩹 First Aid Assistant",
            "💊 Medicine Information",
            "📄 Medical Report Summary",
            "📜 Chat History",
            "ℹ About",
        ],
        index=[
            "🏠 Home",
            "🤒 Symptom Checker",
            "🩹 First Aid Assistant",
            "💊 Medicine Information",
            "📄 Medical Report Summary",
            "📜 Chat History",
            "ℹ About",
        ].index(st.session_state.current_page),
    )
    st.session_state.current_page = nav_option

    st.markdown("---")
    # Status Indicator
    if svcs["gemini"].is_available:
        st.success("🟢 Google Gemini API Connected")
    else:
        st.info("🟡 Knowledge-Base Demo Mode (Offline)")

    st.markdown("---")
    st.warning(
        "🚨 **Emergency Disclaimer:**\n"
        "If you are experiencing severe chest pain, breathing difficulty, or heavy bleeding, "
        "call **911 / 1929** immediately."
    )

# Header Banner
st.markdown(
    """
    <div class="main-header">
        <h1>🩺 MediAssist AI</h1>
        <p>Your Intelligent Emergency Medical Assistant & Health Education Partner</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# PAGE 1: HOME DASHBOARD
# ==========================================
if st.session_state.current_page == "🏠 Home":
    st.subheader("Welcome to MediAssist AI")
    st.write(
        "MediAssist AI uses Google Gemini & Google ADK agent patterns to deliver rapid emergency risk triage, "
        "first-aid instruction, drug safety references, and clinical document summaries."
    )

    # Emergency Hotlines Bar
    st.markdown(
        """
        <div class="emergency-alert-high">
            🚨 <strong>EMERGENCY CONTACT HOTLINES:</strong> &nbsp;|&nbsp; 
            <strong>USA/Canada:</strong> 911 &nbsp;|&nbsp; 
            <strong>Europe/UK:</strong> 112 &nbsp;|&nbsp; 
            <strong>Poison Control (US):</strong> 1-800-222-1222
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <h3>🤒 Symptom Checker</h3>
                <p>Analyze symptoms with patient history and receive educational guidance & urgency assessment.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Symptom Checker", key="btn_symptom"):
            st.session_state.current_page = "🤒 Symptom Checker"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <h3>🩹 First Aid Assistant</h3>
                <p>Instant step-by-step emergency instructions for burns, bleeding, bites, CPR, and fractures.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open First Aid Assistant", key="btn_firstaid"):
            st.session_state.current_page = "🩹 First Aid Assistant"
            st.rerun()

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <h3>💊 Medicine Information</h3>
                <p>Search drug databases for general uses, precautions, and common side effects.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Search Medicines", key="btn_meds"):
            st.session_state.current_page = "💊 Medicine Information"
            st.rerun()

    st.markdown("---")

    col4, col5 = st.columns(2)
    with col4:
        st.markdown(
            """
            <div class="metric-card">
                <h3>📄 Medical Report Summary</h3>
                <p>Upload PDF or TXT reports to extract simplified summaries and abnormal lab values.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Summarize Report", key="btn_report"):
            st.session_state.current_page = "📄 Medical Report Summary"
            st.rerun()

    with col5:
        st.markdown(
            """
            <div class="metric-card">
                <h3>📜 Chat History & Records</h3>
                <p>Review persistent interaction transcripts and export history to JSON or Text files.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Chat History", key="btn_history"):
            st.session_state.current_page = "📜 Chat History"
            st.rerun()


# ==========================================
# PAGE 2: SYMPTOM CHECKER
# ==========================================
elif st.session_state.current_page == "🤒 Symptom Checker":
    st.subheader("🤒 Intelligent Symptom Assessment")
    st.info("Enter patient profile details and symptoms below for educational guidance.")

    with st.form("symptom_form"):
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            duration = st.text_input("Duration of Symptoms", value="2 days")
        with c2:
            med_history = st.text_input("Pre-existing Medical Conditions", placeholder="e.g. Asthma, Diabetes, None")
            medications = st.text_input("Current Medications", placeholder="e.g. Aspirin, Metformin, None")

        symptoms = st.text_area(
            "Describe Current Symptoms *",
            placeholder="e.g., Severe headache with light sensitivity and slight nausea for 4 hours...",
            height=100,
        )

        submitted = st.form_submit_button("🔍 Analyze Symptoms")

    if submitted and symptoms.strip():
        try:
            patient = PatientProfile(
                age=age,
                gender=gender,
                medical_history=med_history,
                current_medications=medications,
            )
            req = SymptomRequest(patient=patient, symptoms=symptoms, duration=duration)

            with st.spinner("Analyzing emergency risk & symptom severity..."):
                # Run agents
                emergency_res = svcs["emergency_agent"].process(symptoms)
                symptom_res = svcs["symptom_agent"].analyze(req)

            # Display Emergency Badge
            st.markdown("### Risk & Urgency Assessment")
            st.markdown(render_severity_badge(emergency_res.severity), unsafe_allow_html=True)

            if emergency_res.severity == "HIGH":
                st.markdown(
                    f"""
                    <div class="emergency-alert-high">
                        🚨 <strong>CRITICAL EMERGENCY ALERT:</strong> {emergency_res.reason}<br>
                        <strong>Recommendation:</strong> {emergency_res.recommendation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif emergency_res.severity == "MEDIUM":
                st.markdown(
                    f"""
                    <div class="emergency-alert-medium">
                        🟡 <strong>MODERATE URGENCY:</strong> {emergency_res.reason}<br>
                        <strong>Recommendation:</strong> {emergency_res.recommendation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Display Analysis Results
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### 💡 Educational Potential Conditions")
                for cond in symptom_res.possible_conditions:
                    st.markdown(f"- **{cond}**")

            with col_b:
                st.markdown("#### 📋 Recommended Action Plan")
                for step in symptom_res.recommended_next_steps:
                    st.markdown(f"1. {step}")

            # In-depth AI Analysis Expander
            if symptom_res.detailed_ai_analysis:
                with st.expander("🤖 Detailed Gemini AI Clinical Assessment & Rationale", expanded=True):
                    st.markdown(symptom_res.detailed_ai_analysis)

            if symptom_res.questions_for_clarification:
                with st.expander("❓ Questions to Discuss with Doctor"):
                    for q in symptom_res.questions_for_clarification:
                        st.write(f"- {q}")

            # Audio TTS
            audio_html = text_to_speech_audio(" ".join(symptom_res.recommended_next_steps[:2]))
            if audio_html:
                st.markdown("##### 🔊 Listen to Summary")
                st.components.v1.html(audio_html, height=60)

            # Disclaimer
            st.warning(symptom_res.disclaimer)

            # Save to Database
            resp_summary = f"Severity: {emergency_res.severity}. Possible: {', '.join(symptom_res.possible_conditions)}"
            svcs["db"].save_chat(
                agent_name="Symptom Agent",
                user_query=symptoms,
                response_content=resp_summary,
                severity=emergency_res.severity,
            )

        except Exception as e:
            st.error(f"Validation Error: {e}")


# ==========================================
# PAGE 3: FIRST AID ASSISTANT
# ==========================================
elif st.session_state.current_page == "🩹 First Aid Assistant":
    st.subheader("🩹 First Aid Guidance & Emergency Steps")
    st.write("Select a common first aid situation or type your emergency topic below:")

    # Quick Action Buttons
    col_fa1, col_fa2, col_fa3, col_fa4 = st.columns(4)
    selected_topic = None
    if col_fa1.button("🔥 Burn First Aid"):
        selected_topic = "burn"
    if col_fa2.button("🐍 Snake Bite"):
        selected_topic = "snake_bite"
    if col_fa3.button("🩸 Severe Bleeding"):
        selected_topic = "heavy_bleeding"
    if col_fa4.button("🫀 CPR Guidance"):
        selected_topic = "cpr_guidance"

    col_fa5, col_fa6, col_fa7, col_fa8 = st.columns(4)
    if col_fa5.button("🦴 Bone Fracture"):
        selected_topic = "fracture"
    if col_fa6.button("🧪 Poisoning"):
        selected_topic = "poisoning"
    if col_fa7.button("🫁 Choking"):
        selected_topic = "choking"
    if col_fa8.button("☀️ Heat Stroke"):
        selected_topic = "heat_stroke"

    user_fa_query = st.text_input("Or enter custom first aid situation:", value=selected_topic or "")

    if user_fa_query:
        with st.spinner("Fetching first aid protocols..."):
            fa_res = svcs["firstaid_agent"].get_first_aid_guide(user_fa_query)

        st.markdown(f"### {fa_res.topic}")
        st.markdown(render_severity_badge(fa_res.severity), unsafe_allow_html=True)

        st.markdown("#### 🔢 Step-by-Step Action Plan:")
        for idx, step in enumerate(fa_res.steps, 1):
            st.markdown(f"**{idx}.** {step}")

        if fa_res.warnings:
            st.error("#### ⚠️ CRITICAL WARNINGS (What NOT to do):")
            for w in fa_res.warnings:
                st.markdown(f"- ❌ {w}")

        st.info(f"🚨 **When to Call Emergency Services:** {fa_res.when_to_call_emergency}")

        # Audio TTS
        audio_html = text_to_speech_audio(f"First aid steps for {fa_res.topic}. " + " ".join(fa_res.steps[:3]))
        if audio_html:
            st.components.v1.html(audio_html, height=60)

        st.warning(fa_res.disclaimer)

        # Save to DB
        svcs["db"].save_chat(
            agent_name="First Aid Agent",
            user_query=user_fa_query,
            response_content=f"Steps: {'; '.join(fa_res.steps[:2])}",
            severity=fa_res.severity,
        )


# ==========================================
# PAGE 4: MEDICINE INFORMATION
# ==========================================
elif st.session_state.current_page == "💊 Medicine Information":
    st.subheader("💊 Educational Medicine Reference")
    st.write("Search drug databases for indications, precautions, side effects, and drug interactions.")

    med_query_text = st.text_input("Search Medicine Name (e.g. Paracetamol, Ibuprofen, Amoxicillin):", value="Paracetamol")

    if med_query_text:
        try:
            m_query = MedicineQuery(query=med_query_text)
            med_results = svcs["medicine_agent"].search_medicine(m_query)

            for med in med_results:
                with st.container():
                    st.markdown(f"### 🧪 {med.name} ({med.category})")

                    st.markdown(f"**Primary Uses:** {med.uses}")

                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        st.markdown("**Common Side Effects:**")
                        for se in med.common_side_effects:
                            st.markdown(f"- {se}")
                    with c_m2:
                        st.markdown("**General Precautions:**")
                        for prec in med.precautions:
                            st.markdown(f"- ⚠️ {prec}")

                    st.markdown(f"**Interactions:** {med.interactions}")
                    st.warning(f"⛔ **Dosage Warning:** {med.dosage_warning}")
                    st.caption(f"📜 {med.disclaimer}")
                    st.markdown("---")

                # Save to DB
                svcs["db"].save_chat(
                    agent_name="Medicine Agent",
                    user_query=med_query_text,
                    response_content=f"Medicine: {med.name}, Uses: {med.uses}",
                    severity="LOW",
                )

        except Exception as e:
            st.error(f"Search Error: {e}")

    # Display Pandas Full Medicine Table
    with st.expander("📊 View Complete Catalog Dataset (Pandas View)"):
        stats = svcs["ks"].get_dataset_stats()
        st.write(f"Total cataloged medicines: {stats.get('total_medicines', 0)}")
        if not svcs["ks"].medicines_df.empty:
            st.dataframe(svcs["ks"].medicines_df, use_container_width=True)


# ==========================================
# PAGE 5: MEDICAL REPORT SUMMARY
# ==========================================
elif st.session_state.current_page == "📄 Medical Report Summary":
    st.subheader("📄 Medical Report Summarizer")
    st.write("Upload a clinical document or lab report (PDF or TXT) to summarize and explain findings.")

    uploaded_file = st.file_uploader("Upload Medical Report (.pdf or .txt)", type=["pdf", "txt"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        success, text_or_err = extract_text_from_file(file_bytes, uploaded_file.name)

        if not success:
            st.error(text_or_err)
        else:
            st.success(f"Successfully loaded {uploaded_file.name} ({len(file_bytes)} bytes)")

            with st.expander("📄 View Extracted Plain Text"):
                st.text(text_or_err[:1500] + ("..." if len(text_or_err) > 1500 else ""))

            if st.button("✨ Summarize Document with AI"):
                with st.spinner("Analyzing medical report text..."):
                    report_res = svcs["report_agent"].summarize_report(text_or_err, uploaded_file.name)

                st.markdown("### AI Summary & Clinical Insights")
                st.markdown(report_res.content)
                st.warning(report_res.disclaimer)

                # Save to DB
                svcs["db"].save_chat(
                    agent_name="Medical Report Agent",
                    user_query=f"Report File: {uploaded_file.name}",
                    response_content=report_res.content[:300] + "...",
                    severity="LOW",
                )


# ==========================================
# PAGE 6: CHAT HISTORY
# ==========================================
elif st.session_state.current_page == "📜 Chat History":
    st.subheader("📜 Saved Chat & Interaction Records")

    # Filters and Actions
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        agent_filter = st.selectbox(
            "Filter by Agent:",
            ["All", "Symptom Agent", "First Aid Agent", "Medicine Agent", "Medical Report Agent"],
        )
    with col_h2:
        export_json = svcs["db"].export_history_json()
        st.download_button(
            "⬇️ Download JSON Transcript",
            data=export_json,
            file_name="mediassist_history.json",
            mime="application/json",
        )
    with col_h3:
        if st.button("🗑️ Clear All History"):
            svcs["db"].clear_history()
            st.success("History cleared successfully!")
            st.rerun()

    history = svcs["db"].get_history(limit=50, agent_filter=agent_filter)

    if not history:
        st.info("No recorded interactions found.")
    else:
        for rec in history:
            with st.expander(f"[{rec['timestamp']}] {rec['agent_name']} - Query: '{rec['user_query'][:30]}...'"):
                st.markdown(render_severity_badge(rec['severity']), unsafe_allow_html=True)
                st.write(f"**User Query:** {rec['user_query']}")
                st.write(f"**Assistant Response:** {rec['response_content']}")


# ==========================================
# PAGE 7: ABOUT
# ==========================================
elif st.session_state.current_page == "ℹ About":
    st.subheader("ℹ About MediAssist AI")
    st.markdown(
        """
        **MediAssist AI** is a state-of-the-art AI-powered Emergency Medical Assistant built for the **Google Developer Groups AI Buildathon**.
        
        ### 🚀 Key Technical Highlights
        - **Google Gemini LLM Integration:** Powered by Google Gemini 1.5 Flash API with custom fallback mechanisms.
        - **Google ADK Agent Patterns:** Modular, single-responsibility agent design (`EmergencyAgent`, `SymptomAgent`, `FirstAidAgent`, `MedicineAgent`, `ReportAgent`).
        - **Pydantic Validation:** Strict data validation schemas for patient records and API requests.
        - **Pandas Data Processing:** Efficient structured dataset querying and health statistics.
        - **Pytest Suite:** Automated unit testing for agents, schemas, services, and fallback behaviors.
        - **SQLite History:** Local database persistence with transcript JSON/TXT export.
        
        ### ⚖️ Legal & Medical Disclaimer
        MediAssist AI is strictly an educational tool and does **NOT** provide medical diagnosis or treatment. 
        Users experiencing emergencies should immediately contact emergency services (911 / 112).
        """
    )
