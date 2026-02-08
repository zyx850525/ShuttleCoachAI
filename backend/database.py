import sqlite3
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime

DB_PATH = "shuttlecoach.db"

class Database:
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                video_path TEXT,
                result_json TEXT,
                error_message TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_task(self, task_id: str, video_path: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analysis_tasks (task_id, status, video_path) VALUES (?, ?, ?)",
            (task_id, "processing", video_path)
        )
        conn.commit()
        conn.close()

    def update_task_result(self, task_id: str, result: Dict[str, Any]):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analysis_tasks SET status = ?, result_json = ? WHERE task_id = ?",
            ("completed", json.dumps(result), task_id)
        )
        conn.commit()
        conn.close()

    def update_task_error(self, task_id: str, error: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analysis_tasks SET status = ?, error_message = ? WHERE task_id = ?",
            ("failed", error, task_id)
        )
        conn.commit()
        conn.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            result = dict(row)
            if result['result_json']:
                result['result'] = json.loads(result['result_json'])
            else:
                result['result'] = None
            
            # Map error_message to error field for frontend compatibility
            if result['error_message']:
                result['error'] = result['error_message']
                
            return result
        return None

    def get_recent_tasks(self, limit: int = 10) -> list:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM analysis_tasks WHERE status = 'completed' ORDER BY created_at DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            task = dict(row)
            if task['result_json']:
                task['result'] = json.loads(task['result_json'])
                results.append(task)
        return results

# Singleton instance
db = Database()
