"""Unit tests for knowledge base datasets and pandas analytics."""

from services.knowledge_service import KnowledgeService


def test_knowledge_base_loading():
    ks = KnowledgeService()
    stats = ks.get_dataset_stats()
    assert stats["total_first_aid_guides"] >= 8
    assert stats["total_medicines"] >= 5
    assert stats["total_diseases_cataloged"] >= 5


def test_disease_symptom_search():
    ks = KnowledgeService()
    matches = ks.search_disease_by_symptom("runny nose and sore throat")
    assert len(matches) > 0
    assert "Cold" in matches[0]["condition"]
