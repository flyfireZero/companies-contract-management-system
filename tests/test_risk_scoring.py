from contract_management.models.clause import Clause, ClauseType
from contract_management.models.contract import Contract
from contract_management.ai.risk_analyzer import RiskAnalyzer
from contract_management.ai.summarizer import ContractSummarizer
from contract_management.models.risk import RiskTier

def test_risk_analyzer_clean_contract():
    analyzer = RiskAnalyzer()
    clean_clauses = [
        Clause(contract_id=1, clause_type=ClauseType.CONFIDENTIALITY, title="Confidentiality", text="Standard mutual terms", risk_score=10.0),
        Clause(contract_id=1, clause_type=ClauseType.LIMITATION_OF_LIABILITY, title="Liability Cap", text="Capped at 12 months fees", risk_score=20.0),
        Clause(contract_id=1, clause_type=ClauseType.TERMINATION, title="Termination", text="30 days notice", risk_score=15.0),
        Clause(contract_id=1, clause_type=ClauseType.GOVERNING_LAW, title="Delaware Law", text="Delaware jurisdiction", risk_score=10.0),
    ]
    assessment = analyzer.evaluate_risk(contract_id=1, clauses=clean_clauses)
    assert assessment.overall_score < 35.0
    assert assessment.risk_tier == RiskTier.LOW
    assert not assessment.requires_general_counsel_approval

def test_risk_analyzer_hazardous_contract():
    analyzer = RiskAnalyzer()
    bad_clauses = [
        Clause(
            contract_id=2,
            clause_type=ClauseType.LIMITATION_OF_LIABILITY,
            title="Unlimited Liability",
            text="Customer agrees to unlimited liability",
            risk_score=95.0,
            risk_explanation="Unlimited liability uncapped"
        ),
        Clause(
            contract_id=2,
            clause_type=ClauseType.INDEMNIFICATION,
            title="One-way Indemnity",
            text="Customer shall indemnify vendor completely",
            risk_score=85.0,
            risk_explanation="One-way indemnity"
        )
    ]
    assessment = analyzer.evaluate_risk(contract_id=2, clauses=bad_clauses)
    assert assessment.overall_score >= 65.0
    assert assessment.risk_tier in [RiskTier.HIGH, RiskTier.CRITICAL]
    assert assessment.requires_general_counsel_approval

def test_executive_summarizer_output():
    c = Contract(
        id=10,
        title="Acme SaaS Platform",
        contract_number="ACM-2026-99",
        counterparty_name="Acme Corp",
        total_value=500000.0,
        currency="USD"
    )
    clauses = [
        Clause(contract_id=10, clause_type=ClauseType.LIMITATION_OF_LIABILITY, title="Liability", text="...", risk_score=30.0)
    ]
    analyzer = RiskAnalyzer()
    assessment = analyzer.evaluate_risk(10, clauses)
    summary = ContractSummarizer.generate_executive_summary(c, clauses, assessment)
    assert "Executive Summary: Acme SaaS Platform" in summary
    assert "ACM-2026-99" in summary
    assert "Overall Risk Score:" in summary
