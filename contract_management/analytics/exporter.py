import csv
import io
import json
from typing import List, Dict, Any
from contract_management.models.contract import Contract
from .stats import PortfolioAnalytics, PortfolioSummary

class ReportExporter:
    """
    Exports contract portfolio audits and metrics to CSV, JSON, and executive Markdown.
    """

    @classmethod
    def export_csv(cls, contracts: List[Contract]) -> str:
        output = io.StringIO()
        fieldnames = [
            "contract_number", "title", "contract_type", "status", "priority",
            "counterparty_name", "total_value", "annual_value", "currency",
            "effective_date", "expiration_date", "auto_renew", "risk_score", "risk_tier"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for c in contracts:
            writer.writerow({
                "contract_number": c.contract_number,
                "title": c.title,
                "contract_type": c.contract_type.value if hasattr(c.contract_type, 'value') else c.contract_type,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "priority": c.priority.value if hasattr(c.priority, 'value') else c.priority,
                "counterparty_name": c.counterparty_name,
                "total_value": c.total_value,
                "annual_value": c.annual_value,
                "currency": c.currency,
                "effective_date": c.effective_date or "",
                "expiration_date": c.expiration_date or "",
                "auto_renew": "YES" if c.auto_renew else "NO",
                "risk_score": c.risk_score,
                "risk_tier": c.risk_tier
            })

        return output.getvalue()

    @classmethod
    def export_json(cls, contracts: List[Contract], summary: PortfolioSummary) -> str:
        data = {
            "summary": summary.__dict__,
            "contracts": [c.to_dict() for c in contracts]
        }
        return json.dumps(data, indent=2, default=str)

    @classmethod
    def export_markdown_report(cls, contracts: List[Contract], summary: PortfolioSummary) -> str:
        md = []
        md.append("# Executive Contract Portfolio & Risk Audit Report")
        md.append(f"- **Total Portfolio Agreements:** {summary.total_contracts}")
        md.append(f"- **Active Agreements:** {summary.active_contracts}")
        md.append(f"- **Total Contract Value (TCV):** ${summary.total_contract_value:,.2f}")
        md.append(f"- **Annual Recurring Spend (ARR):** ${summary.annual_recurring_spend:,.2f}")
        md.append("")
        md.append("## Risk Tier Distribution")
        for tier, count in summary.risk_tier_distribution.items():
            md.append(f"- **{tier}:** {count} agreements")
        md.append("")
        md.append("## Top Counterparties by Financial Exposure")
        for cp in summary.top_counterparties_by_value:
            md.append(f"- **{cp['counterparty']}:** ${cp['total_value']:,.2f}")
        return "\n".join(md)
