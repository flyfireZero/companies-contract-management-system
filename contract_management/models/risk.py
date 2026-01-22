from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from .base import BaseModel

class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class RiskFactor:
    factor_name: str
    clause_type: str
    severity: RiskTier
    score_impact: float
    finding: str
    mitigation_strategy: str

@dataclass
class RiskAssessment(BaseModel):
    id: Optional[int] = None
    contract_id: int = 0
    overall_score: float = 0.0  # 0 to 100
    risk_tier: RiskTier = RiskTier.LOW
    factors: List[RiskFactor] = field(default_factory=list)
    executive_verdict: str = ""
    requires_general_counsel_approval: bool = False
