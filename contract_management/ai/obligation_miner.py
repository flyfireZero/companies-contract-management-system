import re
from typing import List
from contract_management.models.obligation import Obligation, ObligationType, ObligationStatus

class ObligationMiner:
    """
    Mines actionable obligations, payment deadlines, deliverable milestones, and audit requirements.
    """

    DATE_PATTERN = re.compile(r'(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})')
    NET_DAYS_PATTERN = re.compile(r'net\s+(\d{2,3})', re.IGNORECASE)
    DELIVERABLE_WORDS = [r"shall deliver", r"will provide", r"shall submit", r"is required to furnish"]
    AUDIT_WORDS = [r"annual audit", r"soc 2 audit report", r"inspection of records"]

    def mine(self, contract_id: int, text: str) -> List[Obligation]:
        obligations: List[Obligation] = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            s_lower = sentence.lower()

            # 1. Payment Terms
            net_match = self.NET_DAYS_PATTERN.search(s_lower)
            if ("payment" in s_lower or "invoice" in s_lower) and net_match:
                days = net_match.group(1)
                obligations.append(Obligation(
                    contract_id=contract_id,
                    obligation_type=ObligationType.PAYMENT,
                    responsible_party="Internal",
                    title=f"Payment settlement within Net {days} days",
                    description=sentence.strip(),
                    recurrence="MONTHLY",
                    status=ObligationStatus.PENDING
                ))

            # 2. Deliverables
            for d_word in self.DELIVERABLE_WORDS:
                if re.search(d_word, s_lower):
                    dates = self.DATE_PATTERN.findall(sentence)
                    due = dates[0] if dates else None
                    party = "Counterparty" if ("vendor" in s_lower or "contractor" in s_lower) else "Internal"
                    obligations.append(Obligation(
                        contract_id=contract_id,
                        obligation_type=ObligationType.DELIVERABLE,
                        responsible_party=party,
                        title="Service milestone deliverable",
                        description=sentence.strip()[:200],
                        due_date=due,
                        recurrence="ONE_TIME",
                        status=ObligationStatus.PENDING
                    ))
                    break

            # 3. Compliance / Audit
            for a_word in self.AUDIT_WORDS:
                if a_word in s_lower:
                    obligations.append(Obligation(
                        contract_id=contract_id,
                        obligation_type=ObligationType.AUDIT,
                        responsible_party="Counterparty",
                        title="Annual Compliance & Security Audit Submission",
                        description=sentence.strip()[:200],
                        recurrence="ANNUAL",
                        status=ObligationStatus.PENDING
                    ))
                    break

        return obligations
