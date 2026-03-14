from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from contract_management.lifecycle.expiry_engine import ExpiryAlert

@dataclass
class NotificationPayload:
    recipient_email: str
    subject: str
    body: str
    urgency: str
    contract_number: str
    dispatched_at: str

class AlertDispatcher:
    """
    Dispatches expiry, SLA breach, and compliance milestone alerts via Webhook & Email channels.
    """

    @classmethod
    def format_expiry_notification(cls, alert: ExpiryAlert, recipient_email: str = "legal-alerts@company.internal") -> NotificationPayload:
        now = datetime.now(timezone.utc).isoformat()
        subject = f"[{alert.urgency.upper()}] Contract Expiration Notice: {alert.contract_number} ({alert.counterparty_name})"

        lines = [
            f"URGENCY LEVEL: {alert.urgency}",
            f"Contract: {alert.title} ({alert.contract_number})",
            f"Counterparty: {alert.counterparty_name}",
            f"Expiration Date: {alert.expiration_date} ({alert.days_remaining} days remaining)",
            "",
            "ACTION REQUIRED:" if alert.requires_renewal_action else "STATUS NOTICE:",
            "Automated renewal window is active. Please review terms or issue non-renewal notice immediately."
            if alert.requires_renewal_action else
            "Agreement is scheduled to expire naturally without renewal."
        ]

        return NotificationPayload(
            recipient_email=recipient_email,
            subject=subject,
            body="\n".join(lines),
            urgency=alert.urgency,
            contract_number=alert.contract_number,
            dispatched_at=now
        )

    @classmethod
    def dispatch_batch(cls, alerts: List[ExpiryAlert]) -> List[NotificationPayload]:
        dispatched = []
        for a in alerts:
            payload = cls.format_expiry_notification(a)
            dispatched.append(payload)
        return dispatched
