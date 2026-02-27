import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional
from contract_management.models.audit import AuditLogEntry, AuditAction

class AuditLogger:
    """
    Maintains a tamper-evident chain of audit events with SHA-256 verification.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_table()

    def _ensure_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id INTEGER,
                    action TEXT NOT NULL,
                    actor_email TEXT NOT NULL,
                    details TEXT NOT NULL,
                    previous_state TEXT,
                    new_state TEXT,
                    tamper_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

    def _compute_hash(self, prev_hash: str, action: str, details: str, timestamp: str) -> str:
        payload = f"{prev_hash}|{action}|{details}|{timestamp}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def log(
        self,
        action: AuditAction,
        details: str,
        contract_id: Optional[int] = None,
        actor_email: str = "system@enterprise.internal",
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None
    ) -> AuditLogEntry:
        cursor = self.conn.cursor()
        cursor.execute("SELECT tamper_hash FROM audit_logs ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        prev_hash = last_row["tamper_hash"] if last_row and "tamper_hash" in last_row.keys() else "GENESIS_ROOT"

        now = datetime.now(timezone.utc).isoformat()
        tamper_hash = self._compute_hash(prev_hash, action.value, details, now)

        cursor.execute("""
            INSERT INTO audit_logs (
                contract_id, action, actor_email, details, previous_state, new_state,
                tamper_hash, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract_id, action.value, actor_email, details, previous_state, new_state,
            tamper_hash, now, now
        ))
        self.conn.commit()

        return AuditLogEntry(
            id=cursor.lastrowid,
            contract_id=contract_id,
            action=action,
            actor_email=actor_email,
            details=details,
            previous_state=previous_state,
            new_state=new_state,
            tamper_hash=tamper_hash,
            created_at=now,
            updated_at=now
        )

    def verify_chain(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id ASC")
        rows = cursor.fetchall()
        prev_hash = "GENESIS_ROOT"

        for row in rows:
            expected = self._compute_hash(prev_hash, row["action"], row["details"], row["created_at"])
            if expected != row["tamper_hash"]:
                return False
            prev_hash = row["tamper_hash"]
        return True
