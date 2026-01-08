from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .base import BaseModel

class ObligationType(str, Enum):
    PAYMENT = "PAYMENT"
    DELIVERABLE = "DELIVERABLE"
    REPORTING = "REPORTING"
    AUDIT = "AUDIT"
    INSURANCE = "INSURANCE"
    CONFIDENTIALITY = "CONFIDENTIALITY"
    SECURITY_COMPLIANCE = "SECURITY_COMPLIANCE"

class ObligationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"

@dataclass
class Obligation(BaseModel):
    id: Optional[int] = None
    contract_id: int = 0
    obligation_type: ObligationType = ObligationType.DELIVERABLE
    responsible_party: str = "Internal"  # 'Internal' or 'Counterparty'
    title: str = ""
    description: str = ""
    due_date: Optional[str] = None
    recurrence: Optional[str] = None  # 'ONE_TIME', 'MONTHLY', 'QUARTERLY', 'ANNUAL'
    status: ObligationStatus = ObligationStatus.PENDING
    penalty_clause: Optional[str] = None
