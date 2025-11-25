from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority
from contract_management.models.clause import Clause, ClauseType

def test_create_and_fetch_company(company_repo, sample_company):
    fetched = company_repo.get_by_id(sample_company.id)
    assert fetched is not None
    assert fetched.name == "Acme Global Corporation"
    assert fetched.primary_email == "legal@acme.com"

def test_create_and_fetch_contract(contract_repo, sample_company):
    c = Contract(
        title="Master Cloud Services Agreement",
        contract_number="CNT-2025-001",
        contract_type=ContractType.MSA,
        status=ContractStatus.DRAFT,
        priority=Priority.HIGH,
        company_id=sample_company.id,
        counterparty_name=sample_company.name,
        total_value=250000.0,
        annual_value=125000.0,
        effective_date="2025-12-01",
        expiration_date="2027-11-30"
    )
    created = contract_repo.create(c)
    assert created.id is not None

    fetched = contract_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.contract_number == "CNT-2025-001"
    assert fetched.total_value == 250000.0
    assert fetched.status == ContractStatus.DRAFT

def test_contract_status_update(contract_repo, sample_company):
    c = Contract(
        title="Vendor Support Agreement",
        contract_number="CNT-2025-002",
        status=ContractStatus.DRAFT,
        counterparty_name=sample_company.name
    )
    created = contract_repo.create(c)
    assert contract_repo.update_status(created.id, ContractStatus.ACTIVE)

    updated = contract_repo.get_by_id(created.id)
    assert updated.status == ContractStatus.ACTIVE

def test_add_and_retrieve_clauses(contract_repo, sample_company):
    c = contract_repo.create(Contract(
        title="NDA Agreement",
        contract_number="CNT-2025-003",
        counterparty_name=sample_company.name
    ))

    clause = Clause(
        contract_id=c.id,
        clause_type=ClauseType.CONFIDENTIALITY,
        title="Standard 5-Year Confidentiality",
        text="The Receiving Party shall maintain secrecy of all Proprietary Information for 5 years."
    )
    contract_repo.add_clause(clause)

    clauses = contract_repo.get_clauses(c.id)
    assert len(clauses) == 1
    assert clauses[0].clause_type == ClauseType.CONFIDENTIALITY
