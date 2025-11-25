import pytest
import sqlite3
from pathlib import Path
from contract_management.db.connection import DatabaseEngine
from contract_management.db.repositories.company_repo import CompanyRepository
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.models.company import Company, CompanyType
from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority

@pytest.fixture
def memory_db():
    engine = DatabaseEngine(db_path=":memory:")
    conn = engine.get_connection()
    yield conn
    engine.close()

@pytest.fixture
def company_repo(memory_db):
    return CompanyRepository(memory_db)

@pytest.fixture
def contract_repo(memory_db):
    return ContractRepository(memory_db)

@pytest.fixture
def sample_company(company_repo):
    comp = Company(
        name="Acme Global Corporation",
        company_type=CompanyType.VENDOR,
        jurisdiction="California, USA",
        primary_email="legal@acme.com",
        industry="Enterprise Software"
    )
    return company_repo.create(comp)
