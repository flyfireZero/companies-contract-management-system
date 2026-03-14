from contract_management.lifecycle.expiry_engine import ExpiryAlert
from contract_management.notifications.alerts import AlertDispatcher

def test_format_and_dispatch_alert():
    alert = ExpiryAlert(
        contract_id=1,
        contract_number="CNT-2026-X",
        title="Payment Gateway Agreement",
        counterparty_name="PayMaster Corp",
        expiration_date="2026-04-01",
        days_remaining=10,
        urgency="WARNING",
        requires_renewal_action=True
    )
    payload = AlertDispatcher.format_expiry_notification(alert)
    assert payload.urgency == "WARNING"
    assert "PayMaster Corp" in payload.subject
    assert "CNT-2026-X" in payload.body
    assert payload.recipient_email == "legal-alerts@company.internal"
