from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from .base import BaseModel

class CompanyType(str, Enum):
    INTERNAL = "INTERNAL"
    CUSTOMER = "CUSTOMER"
    VENDOR = "VENDOR"
    PARTNER = "PARTNER"
    REGULATOR = "REGULATOR"

@dataclass
class CounterpartyContact:
    name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = None

@dataclass
class Company(BaseModel):
    id: Optional[int] = None
    name: str = ""
    company_type: CompanyType = CompanyType.VENDOR
    jurisdiction: str = "Delaware, USA"
    tax_identifier: Optional[str] = None
    industry: Optional[str] = "Technology"
    primary_email: str = ""
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    risk_rating: str = "LOW"
