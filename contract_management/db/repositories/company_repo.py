import sqlite3
from typing import List, Optional
from datetime import datetime, timezone
from contract_management.models.company import Company, CompanyType

class CompanyRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, company: Company) -> Company:
        now = datetime.now(timezone.utc).isoformat()
        company.created_at = now
        company.updated_at = now
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO companies (
                name, company_type, jurisdiction, tax_identifier,
                industry, primary_email, phone, website, is_active,
                risk_rating, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company.name, company.company_type.value if hasattr(company.company_type, 'value') else company.company_type,
                company.jurisdiction, company.tax_identifier,
                company.industry, company.primary_email, company.phone,
                company.website, 1 if company.is_active else 0,
                company.risk_rating, company.created_at, company.updated_at
            )
        )
        self.conn.commit()
        company.id = cursor.lastrowid
        return company

    def get_by_id(self, company_id: int) -> Optional[Company]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_company(row)

    def get_by_name(self, name: str) -> Optional[Company]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_company(row)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Company]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM companies ORDER BY name ASC LIMIT ? OFFSET ?", (limit, offset))
        return [self._row_to_company(row) for row in cursor.fetchall()]

    def _row_to_company(self, row: sqlite3.Row) -> Company:
        d = dict(row)
        d["company_type"] = CompanyType(d["company_type"])
        d["is_active"] = bool(d["is_active"])
        return Company.from_dict(d)
