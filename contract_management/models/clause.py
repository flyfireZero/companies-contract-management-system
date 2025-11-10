from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .base import BaseModel

class ClauseType(str, Enum):
    CONFIDENTIALITY = "CONFIDENTIALITY"
    INDEMNIFICATION = "INDEMNIFICATION"
    LIMITATION_OF_LIABILITY = "LIMITATION_OF_LIABILITY"
    GOVERNING_LAW = "GOVERNING_LAW"
    TERMINATION = "TERMINATION"
    PAYMENT_TERMS = "PAYMENT_TERMS"
    INTELLECTUAL_PROPERTY = "INTELLECTUAL_PROPERTY"
    DATA_PRIVACY_GDPR = "DATA_PRIVACY_GDPR"
    FORCE_MAJEURE = "FORCE_MAJEURE"
    NON_COMPETE = "NON_COMPETE"
    WARRANTY = "WARRANTY"
    AUDIT_RIGHTS = "AUDIT_RIGHTS"

@dataclass
class Clause(BaseModel):
    id: Optional[int] = None
    contract_id: int = 0
    clause_type: ClauseType = ClauseType.CONFIDENTIALITY
    title: str = ""
    text: str = ""
    page_number: Optional[int] = 1
    section_reference: Optional[str] = None
    is_standard: bool = True
    risk_score: float = 0.0
    risk_explanation: Optional[str] = None
    suggested_revision: Optional[str] = None
