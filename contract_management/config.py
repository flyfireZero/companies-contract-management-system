import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = os.getenv("CCMS_DB_PATH", str(DATA_DIR / "contracts.db"))
STORAGE_DIR = os.getenv("CCMS_STORAGE_DIR", str(DATA_DIR / "storage"))
EXPORTS_DIR = os.getenv("CCMS_EXPORTS_DIR", str(DATA_DIR / "exports"))

DEFAULT_EXPIRY_THRESHOLD_DAYS = [90, 60, 30, 7]
HIGH_RISK_THRESHOLD = 65.0
CRITICAL_RISK_THRESHOLD = 80.0
