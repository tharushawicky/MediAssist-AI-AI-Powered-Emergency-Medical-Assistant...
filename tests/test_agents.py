"""Unit tests for independent AI Agents."""

from agents.emergency_agent import EmergencyDetectionAgent
from agents.firstaid_agent import FirstAidAgent
from agents.medicine_agent import MedicineInformationAgent
from agents.report_agent import MedicalReportSummaryAgent
from agents.symptom_agent import SymptomAnalysisAgent
from models.ai_response import MANDATORY_DISCLAIMER
from models.medicine_model import MedicineQuery
from models.patient import PatientProfile
from models.symptom_request import SymptomRequest


def test_emergency_agent_red_flags():
    agent = EmergencyDetectionAgent()
    assessment = agent.process("Patient has facial drooping, arm weakness, and slurred speech")
    assert assessment.severity == "HIGH"
    assert assessment.disclaimer == MANDATORY_DISCLAIMER


def test_symptom_agent_analysis():
    agent = SymptomAnalysisAgent()
    patient = PatientProfile(age=40, gender="Male")
    req = SymptomRequest(patient=patient, symptoms="Mild headache and sore throat", duration="1 day")
    res = agent.analyze(req)
    assert res.severity == "LOW"
    assert len(res.recommended_next_steps) > 0
    assert res.disclaimer == MANDATORY_DISCLAIMER


def test_firstaid_agent_retrieval():
    agent = FirstAidAgent()
    res = agent.get_first_aid_guide("snake bite")
    assert res.severity == "HIGH"
    assert "Do NOT cut or suck the wound" in str(res.warnings)
    assert res.disclaimer == MANDATORY_DISCLAIMER


def test_medicine_agent_search():
    agent = MedicineInformationAgent()
    query = MedicineQuery(query="Ibuprofen")
    results = agent.search_medicine(query)
    assert len(results) > 0
    assert "Ibuprofen" in results[0].name
    assert len(results[0].dosage_warning) > 0
    assert results[0].disclaimer == MANDATORY_DISCLAIMER


def test_report_agent_summarization():
    agent = MedicalReportSummaryAgent()
    sample_txt = "Patient Name: John Doe\nResult: High blood glucose detected (250 mg/dL). Elevated WBC count."
    res = agent.summarize_report(sample_txt, "lab_report.txt")
    assert res.agent_name == "Medical Report Summary Agent"
    assert len(res.content) > 0
    assert res.disclaimer == MANDATORY_DISCLAIMER
