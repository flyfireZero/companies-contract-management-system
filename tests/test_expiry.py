from datetime import date
from contract_management.models.contract import Contract, ContractStatus
from contract_management.lifecycle.expiry_engine import ExpiryEngine

def test_expiry_engine_evaluation():
    engine = ExpiryEngine()
    as_of = date(2026, 3, 1)

    c1 = Contract(
        id=1,
        title="Vendor SaaS",
        contract_number="VND-001",
        status=ContractStatus.ACTIVE,
        expiration_date="2026-03-05", # 4 days remaining -> CRITICAL
        counterparty_name="CloudHost Inc"
    )
    alert1 = engine.evaluate_contract(c1, as_of=as_of)
    assert alert1 is not None
    assert alert1.urgency == "CRITICAL"
    assert alert1.days_remaining == 4

    c2 = Contract(
        id=2,
        title="Cloud Storage",
        contract_number="VND-002",
        status=ContractStatus.ACTIVE,
        expiration_date="2026-03-25", # 24 days remaining -> WARNING
        counterparty_name="DataStore LLC"
    )
    alert2 = engine.evaluate_contract(c2, as_of=as_of)
    assert alert2 is not None
    assert alert2.urgency == "WARNING"

    c3 = Contract(
        id=3,
        title="Expired Agreement",
        contract_number="VND-003",
        status=ContractStatus.ACTIVE,
        expiration_date="2026-02-15", # -14 days -> EXPIRED
        counterparty_name="OldVendor Co"
    )
    alert3 = engine.evaluate_contract(c3, as_of=as_of)
    assert alert3 is not None
    assert alert3.urgency == "EXPIRED"
