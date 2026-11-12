import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from database.db import get_connection, get_db_cursor
from config.settings import EVENT_COOLDOWN_SECONDS

class EntryLogger:
    """
    Manages audit logging into SQLite entry_logs table with temporal cooldown
    to prevent frame-rate database spam.
    """
    def __init__(self, cooldown_seconds: int = EVENT_COOLDOWN_SECONDS):
        self.cooldown_seconds = cooldown_seconds
        # Maps resident_id (or -1 for unknown) -> last log timestamp (float)
        self._last_logged: Dict[int, float] = {}

    def log_attempt(
        self,
        resident_id: Optional[int],
        match_distance: float,
        decision: str,
        reason: str,
        snapshot_path: Optional[str] = None
    ) -> Optional[int]:
        """
        Inserts an entry log record into SQLite, subject to the cooldown window.
        Returns log_id if recorded, or None if suppressed by cooldown.
        """
        now = time.time()
        key = resident_id if resident_id is not None else -1

        # Check if within cooldown window
        last_time = self._last_logged.get(key, 0.0)
        if (now - last_time) < self.cooldown_seconds:
            return None  # Suppress duplicate event

        # Update last logged time
        self._last_logged[key] = now

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO entry_logs (resident_id, match_distance, decision, reason, snapshot_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (resident_id, float(match_distance), decision, reason, snapshot_path)
            )
            return cursor.lastrowid

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves recent entry logs joined with resident full_name and flat_number.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT l.log_id, l.resident_id, l.timestamp, l.match_distance,
                       l.decision, l.reason, l.snapshot_path,
                       r.full_name, r.flat_number
                FROM entry_logs l
                LEFT JOIN residents r ON l.resident_id = r.resident_id
                ORDER BY l.log_id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_today_summary(self) -> Dict[str, int]:
        """
        Returns aggregated counts of today's attempts by decision type.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            today_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                """
                SELECT decision, COUNT(*) as count
                FROM entry_logs
                WHERE DATE(timestamp) = DATE(?)
                GROUP BY decision
                """,
                (today_date,)
            )
            rows = cursor.fetchall()
            summary = {
                "TOTAL": 0,
                "ENTRY_ALLOWED": 0,
                "ENTRY_REJECTED": 0,
                "VERIFICATION_REQUIRED": 0
            }
            for row in rows:
                dec = row["decision"]
                cnt = row["count"]
                summary[dec] = cnt
                summary["TOTAL"] += cnt
            return summary
        finally:
            conn.close()

    def search_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        decision_filter: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Searches logs with parameterized filtering.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT l.log_id, l.resident_id, l.timestamp, l.match_distance,
                       l.decision, l.reason, l.snapshot_path,
                       r.full_name, r.flat_number
                FROM entry_logs l
                LEFT JOIN residents r ON l.resident_id = r.resident_id
                WHERE 1=1
            """
            params = []

            if start_date:
                sql += " AND DATE(l.timestamp) >= DATE(?)"
                params.append(start_date)
            if end_date:
                sql += " AND DATE(l.timestamp) <= DATE(?)"
                params.append(end_date)
            if decision_filter and decision_filter != "ALL":
                sql += " AND l.decision = ?"
                params.append(decision_filter)
            if query and query.strip():
                pattern = f"%{query.strip()}%"
                sql += " AND (r.full_name LIKE ? OR r.flat_number LIKE ? OR l.reason LIKE ?)"
                params.extend([pattern, pattern, pattern])

            sql += " ORDER BY l.log_id DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

