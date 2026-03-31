import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contract_management.db.connection import get_db, DatabaseEngine
from contract_management.db.repositories.company_repo import CompanyRepository
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.models.company import Company, CompanyType
from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority
from contract_management.models.clause import Clause, ClauseType
from contract_management.ai.risk_analyzer import RiskAnalyzer

def seed_database():
    engine = DatabaseEngine.get_instance()
    engine.init_schema()
    conn = engine.get_connection()
    company_repo = CompanyRepository(conn)
    contract_repo = ContractRepository(conn)
    analyzer = RiskAnalyzer()

    # Seed Companies
    companies_data = [
        Company(name="Apex Cloud Infrastructure Ltd", company_type=CompanyType.VENDOR, jurisdiction="Delaware, USA", primary_email="legal@apexcloud.io", industry="Cloud Infrastructure"),
        Company(name="Global Financial Partners LLC", company_type=CompanyType.CUSTOMER, jurisdiction="New York, USA", primary_email="contracts@globalfin.com", industry="Fintech"),
        Company(name="BioHealth Analytics Inc", company_type=CompanyType.PARTNER, jurisdiction="Massachusetts, USA", primary_email="procurement@biohealth.org", industry="Healthcare"),
        Company(name="CyberShield Security Corp", company_type=CompanyType.VENDOR, jurisdiction="California, USA", primary_email="sec-ops@cybershield.com", industry="Cybersecurity"),
    ]
    created_companies = [company_repo.create(c) for c in companies_data]

    # Seed Contracts
    contracts_data = [
        (
            Contract(
                title="Master Cloud Services Agreement",
                contract_number="CNT-2026-001",
                contract_type=ContractType.MSA,
                status=ContractStatus.ACTIVE,
                priority=Priority.HIGH,
                company_id=created_companies[0].id,
                counterparty_name=created_companies[0].name,
                total_value=360000.0,
                annual_value=120000.0,
                effective_date="2025-06-01",
                expiration_date="2026-04-10", # Expiring soon
                auto_renew=True
            ),
            [
                Clause(contract_id=0, clause_type=ClauseType.LIMITATION_OF_LIABILITY, title="Liability Cap", text="Liability capped at 12 months fees.", risk_score=20.0),
                Clause(contract_id=0, clause_type=ClauseType.CONFIDENTIALITY, title="Mutual Confidentiality", text="5 year mutual non-disclosure.", risk_score=15.0),
                Clause(contract_id=0, clause_type=ClauseType.INDEMNIFICATION, title="IP Indemnification", text="Vendor indemnifies customer for IP infringement.", risk_score=25.0)
            ]
        ),
        (
            Contract(
                title="Enterprise Data Analytics Platform License",
                contract_number="CNT-2026-002",
                contract_type=ContractType.SOFTWARE_LICENSE,
                status=ContractStatus.ACTIVE,
                priority=Priority.CRITICAL,
                company_id=created_companies[1].id,
                counterparty_name=created_companies[1].name,
                total_value=850000.0,
                annual_value=425000.0,
                effective_date="2025-01-15",
                expiration_date="2027-01-15",
                auto_renew=False
            ),
            [
                Clause(contract_id=0, clause_type=ClauseType.DATA_PRIVACY_GDPR, title="Data Protection", text="Standard contractual clauses apply.", risk_score=15.0),
                Clause(contract_id=0, clause_type=ClauseType.PAYMENT_TERMS, title="Payment Terms", text="Net 30 days billing.", risk_score=10.0),
            ]
        ),
        (
            Contract(
                title="Managed SOC & Endpoint Security SLA",
                contract_number="CNT-2026-003",
                contract_type=ContractType.SLA,
                status=ContractStatus.ACTIVE,
                priority=Priority.MEDIUM,
                company_id=created_companies[3].id,
                counterparty_name=created_companies[3].name,
                total_value=145000.0,
                annual_value=145000.0,
                effective_date="2025-09-01",
                expiration_date="2026-05-01", # Expiring in May
                auto_renew=True
            ),
            [
                Clause(contract_id=0, clause_type=ClauseType.LIMITATION_OF_LIABILITY, title="Hazardous Unlimited Liability", text="Vendor liability limited, customer unlimited liability.", risk_score=85.0, risk_explanation="Unilateral unlimited exposure"),
            ]
        )
    ]

    for c, clauses in contracts_data:
        saved = contract_repo.create(c)
        for cl in clauses:
            cl.contract_id = saved.id
            contract_repo.add_clause(cl)
        stored_clauses = contract_repo.get_clauses(saved.id)
        assessment = analyzer.evaluate_risk(saved.id, stored_clauses)
        saved.risk_score = assessment.overall_score
        saved.risk_tier = assessment.risk_tier.value
        contract_repo.update(saved)

    print(f"🎉 Successfully seeded {len(created_companies)} companies and {len(contracts_data)} contracts.")

if __name__ == "__main__":
    seed_database()
