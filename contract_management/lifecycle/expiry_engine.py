from dataclasses import dataclass
from datetime import datetime, date, timezone
from typing import List, Optional
from contract_management.models.contract import Contract, ContractStatus
from contract_management.config import DEFAULT_EXPIRY_THRESHOLD_DAYS

@dataclass
class ExpiryAlert:
    contract_id: int
    contract_number: str
    title: str
    counterparty_name: str
    expiration_date: str
    days_remaining: int
    urgency: str  # NOTICE, WARNING, CRITICAL, EXPIRED
    requires_renewal_action: bool

class ExpiryEngine:
    """
    Scans contracts against a reference date and flags expiring or expired items.
    Supports 90/60/30/7 day alert windows.
    """

    def __init__(self, alert_thresholds: Optional[List[int]] = None):
        self.alert_thresholds = alert_thresholds or DEFAULT_EXPIRY_THRESHOLD_DAYS

    def calculate_days_remaining(self, expiration_date_str: str, as_of: Optional[date] = None) -> int:
        ref_date = as_of or datetime.now(timezone.utc).date()
        exp_date = datetime.strptime(expiration_date_str[:10], "%Y-%m-%d").date()
        return (exp_date - ref_date).days

    def evaluate_contract(self, contract: Contract, as_of: Optional[date] = None) -> Optional[ExpiryAlert]:
        if not contract.expiration_date:
            return None
        if contract.status in [ContractStatus.TERMINATED, ContractStatus.EXPIRED]:
            return None

        days = self.calculate_days_remaining(contract.expiration_date, as_of)

        if days < 0:
            urgency = "EXPIRED"
        elif days <= 7:
            urgency = "CRITICAL"
        elif days <= 30:
            urgency = "WARNING"
        elif days <= 90:
            urgency = "NOTICE"
        else:
            return None

        return ExpiryAlert(
            contract_id=contract.id or 0,
            contract_number=contract.contract_number,
            title=contract.title,
            counterparty_name=contract.counterparty_name,
            expiration_date=contract.expiration_date,
            days_remaining=days,
            urgency=urgency,
            requires_renewal_action=contract.auto_renew or days <= contract.renewal_notice_period_days
        )

    def scan_all(self, contracts: List[Contract], as_of: Optional[date] = None) -> List[ExpiryAlert]:
        alerts = []
        for c in contracts:
            alert = self.evaluate_contract(c, as_of)
            if alert:
                alerts.append(alert)
        alerts.sort(key=lambda a: a.days_remaining)
        return alerts
