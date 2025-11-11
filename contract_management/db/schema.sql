-- Core schema for Companies Contract Management System

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    company_type TEXT NOT NULL DEFAULT 'VENDOR',
    jurisdiction TEXT DEFAULT 'Delaware, USA',
    tax_identifier TEXT,
    industry TEXT DEFAULT 'Technology',
    primary_email TEXT NOT NULL,
    phone TEXT,
    website TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    risk_rating TEXT DEFAULT 'LOW',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    contract_number TEXT NOT NULL UNIQUE,
    contract_type TEXT NOT NULL DEFAULT 'MSA',
    status TEXT NOT NULL DEFAULT 'DRAFT',
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    company_id INTEGER REFERENCES companies(id),
    counterparty_name TEXT NOT NULL,
    owner_department TEXT DEFAULT 'Legal',
    lead_attorney TEXT,
    total_value REAL DEFAULT 0.0,
    annual_value REAL DEFAULT 0.0,
    currency TEXT DEFAULT 'USD',
    payment_terms TEXT DEFAULT 'Net 30',
    effective_date TEXT,
    expiration_date TEXT,
    renewal_notice_period_days INTEGER DEFAULT 30,
    auto_renew INTEGER DEFAULT 0,
    document_hash TEXT,
    file_path TEXT,
    version TEXT DEFAULT '1.0',
    risk_score REAL DEFAULT 0.0,
    risk_tier TEXT DEFAULT 'LOW',
    summary TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clauses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    clause_type TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    page_number INTEGER DEFAULT 1,
    section_reference TEXT,
    is_standard INTEGER DEFAULT 1,
    risk_score REAL DEFAULT 0.0,
    risk_explanation TEXT,
    suggested_revision TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_exp_date ON contracts(expiration_date);
CREATE INDEX IF NOT EXISTS idx_contracts_company_id ON contracts(company_id);
CREATE INDEX IF NOT EXISTS idx_clauses_contract_id ON clauses(contract_id);
