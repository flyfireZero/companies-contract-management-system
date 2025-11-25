import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority
from contract_management.models.clause import Clause, ClauseType

class ContractRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, contract: Contract) -> Contract:
        now = datetime.now(timezone.utc).isoformat()
        contract.created_at = now
        contract.updated_at = now
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO contracts (
                title, contract_number, contract_type, status, priority,
                company_id, counterparty_name, owner_department, lead_attorney,
                total_value, annual_value, currency, payment_terms,
                effective_date, expiration_date, renewal_notice_period_days,
                auto_renew, document_hash, file_path, version,
                risk_score, risk_tier, summary, metadata_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contract.title, contract.contract_number,
                contract.contract_type.value if hasattr(contract.contract_type, 'value') else contract.contract_type,
                contract.status.value if hasattr(contract.status, 'value') else contract.status,
                contract.priority.value if hasattr(contract.priority, 'value') else contract.priority,
                contract.company_id, contract.counterparty_name,
                contract.owner_department, contract.lead_attorney,
                contract.total_value, contract.annual_value,
                contract.currency, contract.payment_terms,
                contract.effective_date, contract.expiration_date,
                contract.renewal_notice_period_days,
                1 if contract.auto_renew else 0,
                contract.document_hash, contract.file_path, contract.version,
                contract.risk_score, contract.risk_tier,
                contract.summary, contract.metadata_json,
                contract.created_at, contract.updated_at
            )
        )
        self.conn.commit()
        contract.id = cursor.lastrowid
        return contract

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_contract(row)

    def get_by_number(self, contract_number: str) -> Optional[Contract]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contracts WHERE contract_number = ?", (contract_number,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_contract(row)

    def update_status(self, contract_id: int, new_status: ContractStatus) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE contracts SET status = ?, updated_at = ? WHERE id = ?",
            (new_status.value if hasattr(new_status, 'value') else new_status, now, contract_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def update(self, contract: Contract) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        contract.updated_at = now
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE contracts SET
                title = ?, contract_type = ?, status = ?, priority = ?,
                company_id = ?, counterparty_name = ?, owner_department = ?,
                lead_attorney = ?, total_value = ?, annual_value = ?,
                currency = ?, payment_terms = ?, effective_date = ?,
                expiration_date = ?, renewal_notice_period_days = ?,
                auto_renew = ?, document_hash = ?, file_path = ?,
                version = ?, risk_score = ?, risk_tier = ?,
                summary = ?, metadata_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                contract.title,
                contract.contract_type.value if hasattr(contract.contract_type, 'value') else contract.contract_type,
                contract.status.value if hasattr(contract.status, 'value') else contract.status,
                contract.priority.value if hasattr(contract.priority, 'value') else contract.priority,
                contract.company_id, contract.counterparty_name,
                contract.owner_department, contract.lead_attorney,
                contract.total_value, contract.annual_value,
                contract.currency, contract.payment_terms,
                contract.effective_date, contract.expiration_date,
                contract.renewal_notice_period_days,
                1 if contract.auto_renew else 0,
                contract.document_hash, contract.file_path,
                contract.version, contract.risk_score, contract.risk_tier,
                contract.summary, contract.metadata_json,
                contract.updated_at, contract.id
            )
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def list_contracts(
        self,
        status: Optional[ContractStatus] = None,
        company_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contract]:
        query = "SELECT * FROM contracts WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status.value if hasattr(status, 'value') else status)
        if company_id:
            query += " AND company_id = ?"
            params.append(company_id)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        return [self._row_to_contract(row) for row in cursor.fetchall()]

    def add_clause(self, clause: Clause) -> Clause:
        now = datetime.now(timezone.utc).isoformat()
        clause.created_at = now
        clause.updated_at = now
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO clauses (
                contract_id, clause_type, title, text, page_number,
                section_reference, is_standard, risk_score, risk_explanation,
                suggested_revision, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clause.contract_id,
                clause.clause_type.value if hasattr(clause.clause_type, 'value') else clause.clause_type,
                clause.title, clause.text, clause.page_number,
                clause.section_reference, 1 if clause.is_standard else 0,
                clause.risk_score, clause.risk_explanation,
                clause.suggested_revision, clause.created_at, clause.updated_at
            )
        )
        self.conn.commit()
        clause.id = cursor.lastrowid
        return clause

    def get_clauses(self, contract_id: int) -> List[Clause]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clauses WHERE contract_id = ? ORDER BY id ASC", (contract_id,))
        clauses = []
        for r in cursor.fetchall():
            d = dict(r)
            d["clause_type"] = ClauseType(d["clause_type"])
            d["is_standard"] = bool(d["is_standard"])
            clauses.append(Clause.from_dict(d))
        return clauses

    def _row_to_contract(self, row: sqlite3.Row) -> Contract:
        d = dict(row)
        d["contract_type"] = ContractType(d["contract_type"])
        d["status"] = ContractStatus(d["status"])
        d["priority"] = Priority(d["priority"])
        d["auto_renew"] = bool(d["auto_renew"])
        return Contract.from_dict(d)
