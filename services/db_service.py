"""SQLite and JSON Chat History persistence service."""

import json
import logging
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("MediAssistAI.DatabaseService")


class ChatDatabaseService:
    """Manages chat history storage in SQLite with export capabilities."""

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "mediassist_chat.db")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return closing(conn)

    def _init_db(self):
        """Creates table if not existing."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT NOT NULL,
                        user_query TEXT NOT NULL,
                        response_content TEXT NOT NULL,
                        severity TEXT DEFAULT 'LOW',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")

    def save_chat(
        self, agent_name: str, user_query: str, response_content: str, severity: str = "LOW"
    ) -> bool:
        """Save a new chat record into database."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO chat_history (agent_name, user_query, response_content, severity, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        agent_name,
                        user_query,
                        response_content,
                        severity,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save chat: {e}")
            return False

    def get_history(self, limit: int = 50, agent_filter: str | None = None) -> list[dict[str, Any]]:
        """Retrieve recent chat history."""
        try:
            with self._get_connection() as conn:
                if agent_filter and agent_filter != "All":
                    cursor = conn.execute(
                        """
                        SELECT id, agent_name, user_query, response_content, severity, timestamp
                        FROM chat_history
                        WHERE agent_name = ?
                        ORDER BY id DESC LIMIT ?
                    """,
                        (agent_filter, limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT id, agent_name, user_query, response_content, severity, timestamp
                        FROM chat_history
                        ORDER BY id DESC LIMIT ?
                    """,
                        (limit,),
                    )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return []

    def clear_history(self) -> bool:
        """Clear all chat history records."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM chat_history")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            return False

    def export_history_json(self) -> str:
        """Export all chat history records as formatted JSON string."""
        history = self.get_history(limit=1000)
        return json.dumps(history, indent=2)

    def export_history_txt(self) -> str:
        """Export all chat history records as plain text transcript."""
        history = self.get_history(limit=1000)
        lines = ["=== MediAssist AI Chat History Transcript ===", ""]
        for record in reversed(history):
            lines.append(f"[{record['timestamp']}] Agent: {record['agent_name']} (Severity: {record['severity']})")
            lines.append(f"User: {record['user_query']}")
            lines.append(f"Assistant: {record['response_content']}")
            lines.append("-" * 50)
        return "\n".join(lines)
