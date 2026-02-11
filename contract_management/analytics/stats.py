from dataclasses import dataclass, field
from typing import List, Dict, Any
from contract_management.models.contract import Contract, ContractStatus, ContractType

@dataclass
class PortfolioSummary:
    total_contracts: int = 0
    active_contracts: int = 0
    total_contract_value: float = 0.0
    annual_recurring_spend: float = 0.0
    avg_contract_value: float = 0.0
    status_distribution: Dict[str, int] = field(default_factory=dict)
    type_distribution: Dict[str, int] = field(default_factory=dict)
    risk_tier_distribution: Dict[str, int] = field(default_factory=dict)
    top_counterparties_by_value: List[Dict[str, Any]] = field(default_factory=list)

class PortfolioAnalytics:
    """
    Computes aggregate metrics, spend exposure, and risk distribution across contract portfolios.
    """

    @classmethod
    def compute_summary(cls, contracts: List[Contract]) -> PortfolioSummary:
        summary = PortfolioSummary()
        summary.total_contracts = len(contracts)

        counterparty_totals: Dict[str, float] = {}

        for c in contracts:
            if c.status == ContractStatus.ACTIVE:
                summary.active_contracts += 1

            summary.total_contract_value += c.total_value
            summary.annual_recurring_spend += c.annual_value

            s_key = c.status.value if hasattr(c.status, 'value') else str(c.status)
            summary.status_distribution[s_key] = summary.status_distribution.get(s_key, 0) + 1

            t_key = c.contract_type.value if hasattr(c.contract_type, 'value') else str(c.contract_type)
            summary.type_distribution[t_key] = summary.type_distribution.get(t_key, 0) + 1

            r_key = c.risk_tier or "LOW"
            summary.risk_tier_distribution[r_key] = summary.risk_tier_distribution.get(r_key, 0) + 1

            cp = c.counterparty_name or "Unknown"
            counterparty_totals[cp] = counterparty_totals.get(cp, 0.0) + c.total_value

        if summary.total_contracts > 0:
            summary.avg_contract_value = round(summary.total_contract_value / summary.total_contracts, 2)

        sorted_cps = sorted(counterparty_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        summary.top_counterparties_by_value = [
            {"counterparty": cp, "total_value": val} for cp, val in sorted_cps
        ]

        return summary
