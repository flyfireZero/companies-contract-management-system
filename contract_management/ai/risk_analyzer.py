from typing import List
from contract_management.models.risk import RiskAssessment, RiskTier, RiskFactor
from contract_management.models.clause import Clause, ClauseType
from contract_management.config import HIGH_RISK_THRESHOLD, CRITICAL_RISK_THRESHOLD

class RiskAnalyzer:
    """
    Analyzes composite contract risk based on extracted clauses, standard posture deviations,
    and missing mandatory protections.
    """

    MANDATORY_CLAUSES = {
        ClauseType.CONFIDENTIALITY: 15.0,
        ClauseType.LIMITATION_OF_LIABILITY: 25.0,
        ClauseType.TERMINATION: 15.0,
        ClauseType.GOVERNING_LAW: 10.0
    }

    def evaluate_risk(self, contract_id: int, clauses: List[Clause]) -> RiskAssessment:
        factors: List[RiskFactor] = []
        clause_map = {c.clause_type: c for c in clauses}
        
        # 1. Missing mandatory protective clauses
        missing_impact = 0.0
        for m_type, penalty in self.MANDATORY_CLAUSES.items():
            if m_type not in clause_map:
                missing_impact += penalty
                factors.append(RiskFactor(
                    factor_name=f"Missing {m_type.value.replace('_', ' ').title()}",
                    clause_type=m_type.value,
                    severity=RiskTier.MEDIUM,
                    score_impact=penalty,
                    finding=f"Contract does not specify a {m_type.value} section.",
                    mitigation_strategy=f"Insert company standard {m_type.value} clause."
                ))

        # 2. Risk from individual clauses
        clause_risk_sum = 0.0
        for clause in clauses:
            if clause.risk_score > 35.0:
                tier = (
                    RiskTier.CRITICAL if clause.risk_score >= 80.0
                    else RiskTier.HIGH if clause.risk_score >= 60.0
                    else RiskTier.MEDIUM
                )
                factors.append(RiskFactor(
                    factor_name=clause.title or clause.clause_type.value,
                    clause_type=clause.clause_type.value,
                    severity=tier,
                    score_impact=clause.risk_score * 0.4,
                    finding=clause.risk_explanation or "Deviation from commercial standard.",
                    mitigation_strategy=clause.suggested_revision or "Negotiate revised standard language."
                ))
                clause_risk_sum += clause.risk_score * 0.4

        total_score = min(100.0, round(missing_impact * 0.5 + clause_risk_sum, 1))

        if total_score >= CRITICAL_RISK_THRESHOLD:
            overall_tier = RiskTier.CRITICAL
            verdict = "REJECT / ESCALATE: Severe liability exposure or missing fundamental legal protections."
            requires_gc = True
        elif total_score >= HIGH_RISK_THRESHOLD:
            overall_tier = RiskTier.HIGH
            verdict = "ELEVATED RISK: Significant revisions required before executive signoff."
            requires_gc = True
        elif total_score >= 40.0:
            overall_tier = RiskTier.MEDIUM
            verdict = "MODERATE RISK: Standard business risk with minor negotiable deviations."
            requires_gc = False
        else:
            overall_tier = RiskTier.LOW
            verdict = "LOW RISK: Meets or exceeds company standard legal guardrails."
            requires_gc = False

        return RiskAssessment(
            contract_id=contract_id,
            overall_score=total_score,
            risk_tier=overall_tier,
            factors=factors,
            executive_verdict=verdict,
            requires_general_counsel_approval=requires_gc
        )
