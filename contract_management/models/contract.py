from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from .base import BaseModel

class ContractType(str, Enum):
    NDA = "NDA"                          # Non-Disclosure Agreement
    MSA = "MSA"                          # Master Services Agreement
    SOW = "SOW"                          # Statement of Work
    SLA = "SLA"                          # Service Level Agreement
    VENDOR_SERVICES = "VENDOR_SERVICES"  # Vendor Procurement
    EMPLOYMENT = "EMPLOYMENT"            # Employment / Contractor
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"# SaaS / On-prem license
    PARTNERSHIP = "PARTNERSHIP"          # Strategic Partnership

class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    PENDING_SIGNATURE = "PENDING_SIGNATURE"
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    RENEWED = "RENEWED"
    TERMINATED = "TERMINATED"

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class Contract(BaseModel):
    id: Optional[int] = None
    title: str = ""
    contract_number: str = ""
    contract_type: ContractType = ContractType.MSA
    status: ContractStatus = ContractStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    
    # Counterparty details
    company_id: Optional[int] = None
    counterparty_name: str = ""
    owner_department: str = "Legal"
    lead_attorney: Optional[str] = None
    
    # Financials
    total_value: float = 0.0
    annual_value: float = 0.0
    currency: str = "USD"
    payment_terms: str = "Net 30"
    
    # Dates
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    renewal_notice_period_days: int = 30
    auto_renew: bool = False
    
    # Document storage & hash
    document_hash: Optional[str] = None
    file_path: Optional[str] = None
    version: str = "1.0"
    
    # AI Analysis & Risk
    risk_score: float = 0.0
    risk_tier: str = "LOW"
    summary: Optional[str] = None
    metadata_json: Optional[str] = None
