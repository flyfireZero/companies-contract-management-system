from typing import List, Dict, Any
from contract_management.models.contract import Contract
from contract_management.models.clause import Clause
from contract_management.models.risk import RiskAssessment

class ContractSummarizer:
    """
    Synthesizes executive legal briefing, counterparty risk exposure, and decision matrix.
    """

    @classmethod
    def generate_executive_summary(
        cls,
        contract: Contract,
        clauses: List[Clause],
        risk: RiskAssessment
    ) -> str:
        lines = []
        lines.append(f"# Executive Summary: {contract.title} ({contract.contract_number})")
        lines.append(f"**Counterparty:** {contract.counterparty_name} | **Type:** {contract.contract_type.value} | **Total Value:** {contract.currency} {contract.total_value:,.2f}")
        lines.append(f"**Term:** {contract.effective_date or 'TBD'} to {contract.expiration_date or 'TBD'} | **Auto-Renew:** {'Yes' if contract.auto_renew else 'No'}")
        lines.append(f"**Overall Risk Score:** {risk.overall_score}/100 ({risk.risk_tier.value})")
        lines.append("")
        lines.append(f"### Verdict & Action Plan")
        lines.append(f"> {risk.executive_verdict}")
        if risk.requires_general_counsel_approval:
            lines.append("> ⚠️ **FLAG:** Mandatory General Counsel sign-off required prior to execution.")
        lines.append("")
        lines.append("### Key Clause Breakdown")
        for c in clauses:
            status_icon = "🟢" if c.risk_score < 40 else "🟡" if c.risk_score < 70 else "🔴"
            lines.append(f"- {status_icon} **{c.clause_type.value}**: {c.title} (Risk: {c.risk_score}/100)")
            if c.risk_explanation and c.risk_score >= 40:
                lines.append(f"  *Finding:* {c.risk_explanation}")
            if c.suggested_revision:
                lines.append(f"  *Suggested Redline:* `{c.suggested_revision}`")

        return "\n".join(lines)
