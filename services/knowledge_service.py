"""Knowledge Service loading JSON files & analyzing datasets using Pandas."""

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger("MediAssistAI.KnowledgeService")


class KnowledgeService:
    """Retrieves structured medical data from JSON datasets and provides Pandas analytics."""

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = data_dir

        self.first_aid_data = self._load_json("first_aid.json", {})
        self.medicines_raw = self._load_json("medicines.json", [])
        self.diseases_raw = self._load_json("diseases.json", [])
        self.emergency_keywords = self._load_json(
            "emergency_keywords.json",
            {"high_severity_keywords": [], "medium_severity_keywords": [], "low_severity_keywords": []},
        )
        self.disclaimer_data = self._load_json("disclaimer.json", {})

        # Build Pandas DataFrames for quick analytics & search
        self.medicines_df = (
            pd.DataFrame(self.medicines_raw) if self.medicines_raw else pd.DataFrame()
        )
        self.diseases_df = pd.DataFrame(self.diseases_raw) if self.diseases_raw else pd.DataFrame()

    def _load_json(self, filename: str, default: Any) -> Any:
        file_path = self.data_dir / filename
        if not file_path.exists():
            logger.warning(f"Data file missing: {file_path}")
            return default
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return default

    def get_first_aid(self, query: str) -> dict[str, Any] | None:
        """Look up first aid guide by keyword or key."""
        cleaned = query.lower().strip()
        # Direct key match
        for key, value in self.first_aid_data.items():
            if key in cleaned or cleaned in key.replace("_", " "):
                return value

        # Search title and steps
        for key, value in self.first_aid_data.items():
            title = value.get("title", "").lower()
            if any(word in title for word in cleaned.split()):
                return value
        return None

    def search_medicine(self, query: str) -> list[dict[str, Any]]:
        """Search medicine DataFrame for matching names, categories, or uses."""
        if self.medicines_df.empty:
            return []

        q = query.lower().strip()
        # Filtering using Pandas str.contains
        mask = (
            self.medicines_df["name"].str.lower().str.contains(q, na=False)
            | self.medicines_df["category"].str.lower().str.contains(q, na=False)
            | self.medicines_df["uses"].str.lower().str.contains(q, na=False)
        )
        matched = self.medicines_df[mask]
        return matched.to_dict(orient="records")

    def search_disease_by_symptom(self, symptom_text: str) -> list[dict[str, Any]]:
        """Find non-diagnostic potential disease matches using symptom keywords."""
        if self.diseases_df.empty:
            return []

        stext = symptom_text.lower()
        results = []
        for _, row in self.diseases_df.iterrows():
            symptoms_list = row.get("common_symptoms", [])
            matches = [s for s in symptoms_list if s.lower() in stext]
            if matches:
                item = row.to_dict()
                item["matched_count"] = len(matches)
                results.append(item)

        results.sort(key=lambda x: x["matched_count"], reverse=True)
        return results

    def get_dataset_stats(self) -> dict[str, Any]:
        """Generate summary statistics using Pandas."""
        stats = {
            "total_first_aid_guides": len(self.first_aid_data),
            "total_medicines": len(self.medicines_df) if not self.medicines_df.empty else 0,
            "total_diseases_cataloged": len(self.diseases_df) if not self.diseases_df.empty else 0,
            "high_severity_keywords_count": len(
                self.emergency_keywords.get("high_severity_keywords", [])
            ),
        }
        if not self.medicines_df.empty and "category" in self.medicines_df.columns:
            stats["medicine_categories"] = (
                self.medicines_df["category"].value_counts().to_dict()
            )
        return stats
