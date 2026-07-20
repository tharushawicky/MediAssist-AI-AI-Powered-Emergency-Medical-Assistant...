"""Unit tests for service layer modules."""

import os
import tempfile

from services.db_service import ChatDatabaseService
from services.emergency_service import EmergencyService
from services.gemini_service import GeminiService
from services.knowledge_service import KnowledgeService


def test_emergency_service_high_risk():
    es = EmergencyService()
    res = es.evaluate_emergency("I am experiencing severe chest pain and difficulty breathing")
    assert res["severity"] == "HIGH"
    assert res["is_emergency"] is True
    assert "Critical" in res["reason"]


def test_emergency_service_low_risk():
    es = EmergencyService()
    res = es.evaluate_emergency("I have a mild runny nose and cough")
    assert res["severity"] == "LOW"
    assert res["is_emergency"] is False


def test_knowledge_service_first_aid():
    ks = KnowledgeService()
    guide = ks.get_first_aid("burn")
    assert guide is not None
    assert "Burn" in guide["title"]
    assert len(guide["steps"]) > 0


def test_knowledge_service_medicine_pandas_search():
    ks = KnowledgeService()
    results = ks.search_medicine("Paracetamol")
    assert len(results) > 0
    assert "Paracetamol" in results[0]["name"]


def test_sqlite_db_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_chat.db")
        db = ChatDatabaseService(db_path=db_path)
        saved = db.save_chat("TestAgent", "User query test", "Agent response test", "LOW")
        assert saved is True

        history = db.get_history()
        assert len(history) == 1
        assert history[0]["agent_name"] == "TestAgent"

        json_export = db.export_history_json()
        assert "TestAgent" in json_export


def test_gemini_service_fallback():
    gs = GeminiService(api_key="invalid_demo_key")
    response = gs.generate_response("Test prompt")
    assert len(response) > 0
    assert "educational" in response.lower()
