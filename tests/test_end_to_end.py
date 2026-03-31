import pytest
from pathlib import Path
from contract_management.db.connection import DatabaseEngine
from contract_management.db.repositories.company_repo import CompanyRepository
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.ingestion.parser import DocumentParser
from contract_management.ai.clause_extractor import ClauseExtractor
from contract_management.ai.risk_analyzer import RiskAnalyzer
from contract_management.ai.summarizer import ContractSummarizer
from contract_management.lifecycle.state_machine import ContractStateMachine
from contract_management.lifecycle.expiry_engine import ExpiryEngine
from contract_management.analytics.stats import PortfolioAnalytics
from contract_management.models.company import Company, CompanyType
from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority
from contract_management.models.clause import Clause

def test_full_enterprise_contract_lifecycle(memory_db):
    company_repo = CompanyRepository(memory_db)
    contract_repo = ContractRepository(memory_db)

    # 1. Register Counterparty
    company = company_repo.create(Company(
        name="NextGen Logistics Corp",
        company_type=CompanyType.VENDOR,
        jurisdiction="Delaware, USA",
        primary_email="contracts@nextgen.com"
    ))
    assert company.id is not None

    # 2. Ingest & Parse Sample Document
    parser = DocumentParser()
    msa_path = Path("data/samples/sample_msa.txt")
    parsed_doc = parser.parse_file(str(msa_path))
    assert len(parsed_doc.sections) >= 5

    # 3. Create Contract Record in Draft State
    contract = contract_repo.create(Contract(
        title=parsed_doc.title,
        contract_number="E2E-MSA-2026",
        contract_type=ContractType.MSA,
        status=ContractStatus.DRAFT,
        company_id=company.id,
        counterparty_name=company.name,
        total_value=120000.0,
        annual_value=60000.0,
        effective_date="2026-01-01",
        expiration_date="2026-04-15",
        auto_renew=True
    ))

    # 4. Extract Clauses & Assess Risk
    extractor = ClauseExtractor()
    extracted_clauses = extractor.extract_from_sections(parsed_doc.sections)
    assert len(extracted_clauses) >= 4

    for ec in extracted_clauses:
        contract_repo.add_clause(Clause(
            contract_id=contract.id,
            clause_type=ec.clause_type,
            title=ec.title,
            text=ec.text,
            risk_score=ec.risk_score
        ))

    stored_clauses = contract_repo.get_clauses(contract.id)
    analyzer = RiskAnalyzer()
    risk_assessment = analyzer.evaluate_risk(contract.id, stored_clauses)
    assert risk_assessment.overall_score >= 0.0

    # 5. Lifecycle Transitions (DRAFT -> IN_REVIEW -> APPROVED -> PENDING_SIGNATURE -> ACTIVE)
    ContractStateMachine.transition(contract, ContractStatus.IN_REVIEW)
    ContractStateMachine.transition(contract, ContractStatus.APPROVED)
    ContractStateMachine.transition(contract, ContractStatus.PENDING_SIGNATURE)
    ContractStateMachine.transition(contract, ContractStatus.ACTIVE)
    contract_repo.update_status(contract.id, ContractStatus.ACTIVE)

    updated_contract = contract_repo.get_by_id(contract.id)
    assert updated_contract.status == ContractStatus.ACTIVE

    # 6. Expiry Radar Evaluation
    from datetime import date
    engine = ExpiryEngine()
    alert = engine.evaluate_contract(updated_contract, as_of=date(2026, 3, 25))
    assert alert is not None
    assert alert.days_remaining == 21
    assert alert.urgency == "WARNING"

    # 7. Portfolio Analytics
    summary = PortfolioAnalytics.compute_summary([updated_contract])
    assert summary.total_contracts == 1
    assert summary.active_contracts == 1
    assert summary.total_contract_value == 120000.0
