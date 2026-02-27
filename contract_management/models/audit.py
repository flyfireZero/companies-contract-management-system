from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .base import BaseModel

class AuditAction(str, Enum):
    CONTRACT_CREATED = "CONTRACT_CREATED"
    STATUS_TRANSITION = "STATUS_TRANSITION"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    CLAUSE_EXTRACTED = "CLAUSE_EXTRACTED"
    RISK_ASSESSED = "RISK_ASSESSED"
    AMENDMENT_ADDED = "AMENDMENT_ADDED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"

@dataclass
class AuditLogEntry(BaseModel):
    id: Optional[int] = None
    contract_id: Optional[int] = None
    action: AuditAction = AuditAction.CONTRACT_CREATED
    actor_email: str = "system@enterprise.internal"
    details: str = ""
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    tamper_hash: Optional[str] = None
