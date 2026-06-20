import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.utils.logger import logger

class DBClient:
    def __init__(self, db_path: str = "competitors.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competitor_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    pricing_data TEXT NOT NULL,
                    features_data TEXT NOT NULL,
                    trace_id TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully.")

    def save_snapshot(self, competitor_id: str, pricing_data: Dict[str, Any], features_data: List[str], trace_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO snapshots (competitor_id, timestamp, pricing_data, features_data, trace_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                competitor_id,
                datetime.utcnow().isoformat(),
                json.dumps(pricing_data),
                json.dumps(features_data),
                trace_id
            ))
            conn.commit()
            logger.info(f"Snapshot saved for competitor: {competitor_id}")

    def get_latest_snapshot(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pricing_data, features_data, timestamp, trace_id
                FROM snapshots
                WHERE competitor_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (competitor_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "pricing_data": json.loads(row["pricing_data"]),
                    "features_data": json.loads(row["features_data"]),
                    "timestamp": row["timestamp"],
                    "trace_id": row["trace_id"]
                }
            return None

    def get_snapshot_history(self, competitor_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pricing_data, features_data, timestamp, trace_id
                FROM snapshots
                WHERE competitor_id = ?
                ORDER BY timestamp DESC
            """, (competitor_id,))
            rows = cursor.fetchall()
            return [
                {
                    "pricing_data": json.loads(row["pricing_data"]),
                    "features_data": json.loads(row["features_data"]),
                    "timestamp": row["timestamp"],
                    "trace_id": row["trace_id"]
                }
                for row in rows
            ]
