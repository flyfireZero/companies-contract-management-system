from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class ContractCreateRequest:
    title: str
    contract_number: str
    counterparty_name: str
    contract_type: str = "MSA"
    total_value: float = 0.0
    annual_value: float = 0.0
    currency: str = "USD"
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    auto_renew: bool = False

@dataclass
class APIResponse:
    success: bool
    data: Any = None
    error: Optional[str] = None
