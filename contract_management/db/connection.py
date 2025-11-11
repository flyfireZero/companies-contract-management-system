import sqlite3
import threading
from pathlib import Path
from typing import Optional
from contract_management.config import DATABASE_PATH, BASE_DIR

class DatabaseEngine:
    _instance: Optional["DatabaseEngine"] = None
    _lock = threading.Lock()

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self.init_schema()

    @classmethod
    def get_instance(cls, db_path: str = DATABASE_PATH) -> "DatabaseEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            self._local.conn = conn
        return self._local.conn

    def init_schema(self):
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                ddl = f.read()
            conn = self.get_connection()
            with conn:
                conn.executescript(ddl)

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

def get_db(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    return DatabaseEngine.get_instance(db_path).get_connection()
